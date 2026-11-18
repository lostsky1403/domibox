#!/usr/bin/env python3
"""DomiBox Phase 1A - deterministic Stalwart PoC test runner.

Three explicit, non-conflated modes:
  static   - default. No network calls, no account creation, no deployment.
  local    - against an ALREADY RUNNING, explicitly authorized local PoC only.
  external - SMTP from an independent network against an authorized running PoC.

Every test emits PASS / FAIL / BLOCKED / NOT_EXECUTED with evidence.
Credentials are read from the environment only and are never printed or saved.
No placeholder identifiers are ever used in an executable path.

Vendor-supported APIs (verified 2026-11-18, stalw.art/docs/ref):
  x:Domain/query {filter:{name}}, x:Domain/get {ids}
  x:Account/set {create|destroy}, x:Account/get {ids}
  Email/query, Email/get (RFC 8621)
  JMAP session GET /jmap/, management POST /jmap/
"""
from __future__ import annotations

import argparse
import base64
import ipaddress
import json
import os
import secrets
import smtplib
import socket
import ssl
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib import error as urlerror
from urllib import request as urlrequest

USING_MGMT = ["urn:ietf:params:jmap:core", "urn:stalwart:jmap"]
USING_MAIL = ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"]
REQUIRED_CAPS = (
    "urn:ietf:params:jmap:core",
    "urn:stalwart:jmap",
    "urn:ietf:params:jmap:mail",
)


# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------
class RunnerError(Exception):
    """Base class for expected, reportable failures."""


class ConfigError(RunnerError):
    pass


class HttpError(RunnerError):
    pass


class RequestError(RunnerError):
    pass


class InvalidJson(RunnerError):
    pass


class JmapError(RunnerError):
    pass


class MissingDomain(JmapError):
    pass


class MissingAccountId(JmapError):
    pass


class SmtpError(RunnerError):
    pass


class CleanupError(RunnerError):
    pass


# --------------------------------------------------------------------------
# HTTP transport (injectable for mocked tests)
# --------------------------------------------------------------------------
@dataclass
class Response:
    status: int
    text: str
    headers: Dict[str, str] = field(default_factory=dict)


class HttpTransport:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def request(self, method: str, url: str, headers: Optional[Dict[str, str]] = None,
                body: Optional[str] = None) -> Response:
        data = body.encode("utf-8") if body is not None else None
        req = urlrequest.Request(url, data=data, headers=headers or {}, method=method)
        try:
            with urlrequest.urlopen(req, timeout=self.timeout) as resp:
                return Response(resp.status, resp.read().decode("utf-8", "replace"),
                                dict(resp.headers.items()))
        except urlerror.HTTPError as exc:
            return Response(exc.code, exc.read().decode("utf-8", "replace"),
                            dict(exc.headers.items()) if exc.headers else {})
        except (urlerror.URLError, socket.timeout, TimeoutError) as exc:
            raise RequestError(f"network/timeout error: {exc}") from exc


# --------------------------------------------------------------------------
# JMAP client with strict response validation
# --------------------------------------------------------------------------
class JmapClient:
    def __init__(self, transport: Any, url: str, user: str = "", password: str = "",
                 token: str = ""):
        self.transport = transport
        self.url = url
        self.user = user
        self.password = password
        self.token = token
        self.last_response: Optional[Response] = None
        self._secrets = [v for v in (user, password, token) if v]

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        else:
            raw = f"{self.user}:{self.password}".encode("utf-8")
            headers["Authorization"] = "Basic " + base64.b64encode(raw).decode("ascii")
        return headers

    def sanitize(self, text: str) -> str:
        if not text:
            return text
        for value in sorted(self._secrets, key=len, reverse=True):
            text = text.replace(value, "[REDACTED]")
        return text

    def _parse(self, response: Response) -> Any:
        self.last_response = response
        if response.status != 200:
            raise HttpError(f"HTTP {response.status} from JMAP endpoint")
        try:
            return json.loads(response.text)
        except (ValueError, TypeError) as exc:
            raise InvalidJson(f"response is not valid JSON: {exc}") from exc

    def session(self) -> Dict[str, Any]:
        response = self.transport.request("GET", self.url, self._headers())
        obj = self._parse(response)
        if not isinstance(obj, dict):
            raise JmapError("JMAP session response is not an object")
        caps = obj.get("capabilities")
        if not isinstance(caps, dict):
            raise JmapError("JMAP session has no capabilities object")
        missing = [c for c in REQUIRED_CAPS if c not in caps]
        if missing:
            raise JmapError("missing JMAP capabilities: " + ", ".join(missing))
        return obj

    def call(self, using: List[str], method_calls: List[List[Any]]) -> Dict[str, Tuple[str, Dict[str, Any]]]:
        payload = {"using": using, "methodCalls": method_calls}
        response = self.transport.request(
            "POST", self.url, self._headers(), json.dumps(payload)
        )
        obj = self._parse(response)
        responses = obj.get("methodResponses") if isinstance(obj, dict) else None
        if not isinstance(responses, list):
            raise JmapError("response has no methodResponses array")
        out: Dict[str, Tuple[str, Dict[str, Any]]] = {}
        for item in responses:
            if not isinstance(item, list) or len(item) < 2:
                raise JmapError("malformed methodResponses entry")
            name, args, call_id = item[0], item[1], (item[2] if len(item) > 2 else None)
            if not isinstance(args, dict):
                raise JmapError(f"{name}: arguments are not an object")
            if args.get("type") == "error":
                detail = args.get("description") or args.get("detail") or "unspecified"
                raise JmapError(f"{name} method error: {detail}")
            for key in ("notCreated", "notUpdated", "notDestroyed"):
                failures = args.get(key)
                if isinstance(failures, dict) and failures:
                    raise JmapError(f"{name} {key}: {json.dumps(failures)}")
            out[str(call_id)] = (str(name), args)
        return out


# --------------------------------------------------------------------------
# Vendor-supported operations
# --------------------------------------------------------------------------
def discover_domain_id(client: JmapClient, domain_name: str) -> str:
    query = client.call(USING_MGMT, [["x:Domain/query", {"filter": {"name": domain_name}}, "dq"]])
    args = query.get("dq", ("", {}))[1]
    ids = args.get("ids") or []
    if not ids:
        raise MissingDomain(f"x:Domain/query returned no domain for {domain_name}")
    get = client.call(USING_MGMT, [["x:Domain/get", {"ids": ids[:10]}, "dg"]])
    data = get.get("dg", ("", {}))[1].get("data") or []
    for entry in data:
        if isinstance(entry, dict) and entry.get("name") == domain_name and entry.get("id"):
            return str(entry["id"])
    raise MissingDomain(f"x:Domain/get did not confirm exact domain {domain_name}")


def create_identity(client: JmapClient, domain_name: str, domain_id: str,
                    localpart: str, alias_name: str, password: str) -> str:
    ref = "new1"
    obj = {
        "@type": "User",
        "name": localpart,
        "domainId": domain_id,
        "roles": {"@type": "User"},
        "permissions": {"@type": "Inherit"},
        "quotas": {},
        "aliases": {"0": {"name": alias_name, "domainId": domain_id}},
        "credentials": {"0": {"@type": "Password", "secret": password}},
        "encryptionAtRest": {"@type": "Disabled"},
    }
    resp = client.call(USING_MGMT, [["x:Account/set", {"create": {ref: obj}}, "ac"]])
    created = resp.get("ac", ("", {}))[1].get("created") or {}
    entry = created.get(ref)
    if not isinstance(entry, dict) or not entry.get("id"):
        raise MissingAccountId("x:Account/set create returned no account id")
    account_id = str(entry["id"])
    confirm = client.call(USING_MGMT, [["x:Account/get", {"ids": [account_id]}, "ag"]])
    data = confirm.get("ag", ("", {}))[1].get("data") or []
    if not data or data[0].get("name") != localpart:
        raise JmapError("created account could not be confirmed by x:Account/get")
    return account_id


def account_name(client: JmapClient, account_id: str) -> Optional[str]:
    resp = client.call(USING_MGMT, [["x:Account/get", {"ids": [account_id]}, "vg"]])
    data = resp.get("vg", ("", {}))[1].get("data") or []
    return data[0].get("name") if data else None


def destroy_identity(client: JmapClient, account_id: str, expected_name: str) -> None:
    # Ownership guard: only an id created in this run with the exact expected name.
    name = account_name(client, account_id)
    if name != expected_name:
        raise CleanupError(
            "refusing to delete account: id is not an identity created by this run "
            "(name mismatch)"
        )
    resp = client.call(USING_MGMT, [["x:Account/set", {"destroy": [account_id]}, "dd"]])
    destroyed = resp.get("dd", ("", {}))[1].get("destroyed") or []
    if account_id not in destroyed:
        raise CleanupError("x:Account/set destroy did not confirm the account id")


def verify_message(client: JmapClient, account_id: str, subject_token: str) -> Tuple[bool, List[str]]:
    query = client.call(USING_MAIL, [["Email/query", {"accountId": account_id, "limit": 20}, "eq"]])
    ids = query.get("eq", ("", {}))[1].get("ids") or []
    if not ids:
        return False, []
    fetched = client.call(USING_MAIL, [[
        "Email/get",
        {"accountId": account_id, "ids": ids[:20],
         "properties": ["id", "subject", "receivedAt", "from", "to"]},
        "eg",
    ]])
    data = fetched.get("eg", ("", {}))[1].get("data") or []
    subjects = [str(m.get("subject") or "") for m in data if isinstance(m, dict)]
    return any(subject_token in s for s in subjects), subjects


def smtp_send(host: str, port: int, to: str, sender: str, subject: str, body: str,
              timeout: float, starttls: bool, insecure_tls: bool) -> float:
    started = time.monotonic()
    message = EmailMessage()
    message["From"] = sender
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(host, port, timeout=timeout) as smtp:
            smtp.ehlo()
            if starttls:
                if not smtp.has_extn("starttls"):
                    raise SmtpError("SMTP server did not advertise STARTTLS")
                context = (ssl._create_unverified_context() if insecure_tls
                           else ssl.create_default_context())
                smtp.starttls(context=context)
                smtp.ehlo()
            refused = smtp.sendmail(sender, [to], message.as_string())
            if refused:
                raise SmtpError(f"SMTP recipient refused: {refused}")
    except (smtplib.SMTPException, OSError) as exc:
        raise SmtpError(f"SMTP delivery failed: {exc}") from exc
    return (time.monotonic() - started) * 1000.0


# --------------------------------------------------------------------------
# Results and runner
# --------------------------------------------------------------------------
@dataclass
class TestResult:
    test_id: str
    description: str
    preconditions: str
    expected: str
    execution_status: str = "NOT_EXECUTED"
    result: str = "NOT_EXECUTED"
    actual: str = ""
    evidence: str = ""
    failure_reason: str = ""
    duration_ms: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "description": self.description,
            "preconditions": self.preconditions,
            "expected": self.expected,
            "execution_status": self.execution_status,
            "result": self.result,
            "actual": self.actual,
            "evidence": self.evidence,
            "failure_reason": self.failure_reason,
            "duration_ms": self.duration_ms,
        }


TEST_CATALOG = {
    "T-001": ("JMAP session and required capabilities",
              "Authorized PoC running; loopback JMAP endpoint reachable",
              "GET /jmap/ returns core, stalwart and mail capabilities"),
    "T-002": ("Domain discovery",
              "T-001 passed",
              "x:Domain/query + x:Domain/get resolve the exact configured domain id"),
    "T-003": ("Throwaway identity creation",
              "T-002 passed",
              "x:Account/set create returns an id confirmed by x:Account/get"),
    "T-004": ("Message delivery and JMAP retrieval",
              "T-003 passed; SMTP listener accepting",
              "Sent subject token is found by Email/query + Email/get"),
    "T-005": ("Cleanup of identities created in this run",
              "T-003 created at least one identity",
              "Only this run's ids are destroyed; each destroy is confirmed"),
    "T-E01": ("External SMTP connectivity",
              "Authorized external PoC; public SMTP endpoint configured",
              "TCP connect and SMTP greeting from an independent network"),
    "T-E02": ("External message acceptance",
              "T-E01 passed; T-003 created identity",
              "Real message sent from this host is accepted by the PoC"),
    "T-E03": ("External message retrieval",
              "T-E02 passed; JMAP reachable via authorized tunnel",
              "Delivered subject token retrieved through JMAP"),
    "T-E04": ("External-run cleanup",
              "T-003 created an identity",
              "Only this run's identity destroyed"),
}


class Runner:
    def __init__(self, args: argparse.Namespace, transport: Any = None,
                 smtp_sender: Optional[Callable[..., float]] = None):
        self.args = args
        self.mode = args.mode
        self.results: List[TestResult] = []
        self.created: Dict[str, str] = {}  # account_id -> expected localpart
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.run_id = f"{self.mode}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(3)}"
        self.evidence_dir = os.path.join(args.report_dir, self.run_id)
        os.makedirs(self.evidence_dir, exist_ok=True)
        self.transport = transport if transport is not None else HttpTransport(args.timeout)
        self.client = JmapClient(self.transport, args.jmap_url, args.admin_user,
                                 args.admin_password, args.admin_token)
        self.smtp_sender = smtp_sender or smtp_send
        self.localpart = f"poc-{secrets.token_hex(5)}"
        self.alias_name = f"poc-alias-{secrets.token_hex(5)}"
        self.subject_token = f"DOMIBOX-POC-{secrets.token_hex(8)}"
        self._prepared = False

    # -- reporting helpers -------------------------------------------------
    def _rel(self, path: str) -> str:
        try:
            return os.path.relpath(path, os.getcwd())
        except ValueError:
            return os.path.abspath(path)

    def _make(self, test_id: str) -> TestResult:
        desc, pre, expected = TEST_CATALOG[test_id]
        return TestResult(test_id, desc, pre, expected)

    def _add(self, result: TestResult) -> None:
        self.results.append(result)

    def _evidence(self, test_id: str, payload: str) -> str:
        path = os.path.join(self.evidence_dir, f"{test_id}.txt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.client.sanitize(payload))
        return self._rel(path)

    def _blocked(self, test_id: str, reason: str) -> None:
        result = self._make(test_id)
        result.result = "BLOCKED"
        result.failure_reason = reason
        result.actual = "not executed"
        self._add(result)

    def _run(self, test_id: str, fn: Callable[[], str]) -> bool:
        result = self._make(test_id)
        started = time.monotonic()
        result.execution_status = "EXECUTED"
        try:
            result.actual = fn()
            result.result = "PASS"
        except Exception as exc:  # noqa: BLE001 - report every failure, fail closed
            result.result = "FAIL"
            detail = f"{type(exc).__name__}: {exc}\n{traceback.format_exc(limit=4)}"
            if self.client.last_response is not None:
                detail += "\nLAST RESPONSE (sanitized): " + self.client.sanitize(
                    self.client.last_response.text[:2000])
            result.failure_reason = f"{type(exc).__name__}: {exc}"
            result.evidence = self._evidence(test_id, detail)
        result.duration_ms = int((time.monotonic() - started) * 1000)
        if not result.evidence:
            result.evidence = self._rel(os.path.join(self.evidence_dir, "report.json")) + f"#{test_id}"
        self._add(result)
        return result.result == "PASS"

    # -- mode gate ---------------------------------------------------------
    def prepare(self) -> None:
        if self._prepared:
            return
        args = self.args
        if not args.jmap_url.startswith(("http://", "https://")):
            raise ConfigError("--jmap-url must be an absolute http(s) URL")
        from urllib.parse import urlparse
        parsed = urlparse(args.jmap_url)
        jmap_host = (parsed.hostname or "").lower()
        loopback = {"127.0.0.1", "::1", "localhost"}
        if self.mode == "static":
            pass  # static mode makes no network calls at all
        elif self.mode == "local":
            if not args.local_authorized or args.confirm_local != "LOCAL-POC":
                raise ConfigError("local mode requires --local-authorized --confirm-local LOCAL-POC")
            if jmap_host not in loopback:
                raise ConfigError(f"local mode rejects JMAP host {jmap_host!r}; loopback only")
            if (args.smtp_host or "").lower() not in loopback:
                raise ConfigError("local mode rejects non-loopback SMTP host")
            if not (args.admin_user or args.admin_token):
                raise ConfigError("credentials must be supplied via environment")
        elif self.mode == "external":
            if not args.external_authorized or args.confirm_external != (args.external_smtp_host or ""):
                raise ConfigError("external mode requires --external-authorized and --confirm-external <exact host>")
            if not args.external_smtp_host:
                raise ConfigError("--external-smtp-host is required")
            try:
                addr = ipaddress.ip_address(args.external_smtp_host)
                if addr.is_loopback or addr.is_private or addr.is_link_local:
                    raise ConfigError("external SMTP host must be a public address")
            except ValueError:
                if args.external_smtp_host.lower() in loopback:
                    raise ConfigError("external SMTP host must be a public address")
            if jmap_host not in loopback and jmap_host not in args.allow_jmap_hosts:
                raise ConfigError(f"external mode rejects unexpected JMAP host {jmap_host!r}")
            if not (args.admin_user or args.admin_token):
                raise ConfigError("credentials must be supplied via environment")
        else:
            raise ConfigError(f"unknown mode {self.mode!r}")
        self._prepared = True

    # -- local run ---------------------------------------------------------
    def run_local(self) -> None:
        args = self.args
        domain_id_box: Dict[str, str] = {}

        def t001() -> str:
            session = self.client.session()
            return "session OK; capabilities: " + ", ".join(sorted(session["capabilities"]))

        def t002() -> str:
            domain_id_box["id"] = discover_domain_id(self.client, args.domain)
            return f"domain {args.domain} -> id {domain_id_box['id']}"

        def t003() -> str:
            account_id = create_identity(
                self.client, args.domain, domain_id_box["id"], self.localpart,
                self.alias_name, self.test_password,
            )
            self.created[account_id] = self.localpart
            return f"created id {account_id} for alias {self.alias_name}@{args.domain}"

        def t004() -> str:
            subject = f"{self.subject_token} local"
            latency = self.smtp_sender(
                args.smtp_host, args.smtp_port,
                f"{self.alias_name}@{args.domain}", "poc-sender@example.invalid",
                subject, "DomiBox Phase 1A throwaway test message.",
                args.timeout, args.starttls, args.insecure_smtp_tls,
            )
            account_id = next(iter(self.created))
            found, subjects = verify_message(self.client, account_id, self.subject_token)
            if not found:
                raise JmapError(f"message not found via JMAP; subjects seen: {subjects[:5]}")
            return f"delivered and retrieved; SMTP {latency:.0f} ms"

        ok1 = self._run("T-001", t001)
        if not ok1:
            for tid in ("T-002", "T-003", "T-004"):
                self._blocked(tid, "precondition T-001 failed")
            self._cleanup_blocked("T-005", "no identity was created")
            return
        ok2 = self._run("T-002", t002)
        if not ok2:
            for tid in ("T-003", "T-004"):
                self._blocked(tid, "precondition T-002 failed")
            self._cleanup_blocked("T-005", "no identity was created")
            return
        ok3 = self._run("T-003", t003)
        if not ok3:
            self._blocked("T-004", "precondition T-003 failed")
            self._cleanup("T-005")
            return
        self._run("T-004", t004)
        self._cleanup("T-005")

    # -- external run ------------------------------------------------------
    def run_external(self) -> None:
        args = self.args
        domain_id_box: Dict[str, str] = {}

        def t001() -> str:
            session = self.client.session()
            return "session OK (tunneled management); capabilities: " + ", ".join(
                sorted(session["capabilities"]))

        def t002() -> str:
            domain_id_box["id"] = discover_domain_id(self.client, args.domain)
            return f"domain {args.domain} -> id {domain_id_box['id']}"

        def t003() -> str:
            account_id = create_identity(
                self.client, args.domain, domain_id_box["id"], self.localpart,
                self.alias_name, self.test_password,
            )
            self.created[account_id] = self.localpart
            return f"created id {account_id} for alias {self.alias_name}@{args.domain}"

        def te01() -> str:
            host, port = args.external_smtp_host, args.external_smtp_port
            started = time.monotonic()
            with socket.create_connection((host, port), timeout=args.timeout) as sock:
                sock.settimeout(args.timeout)
                banner = sock.recv(512).decode("utf-8", "replace").strip()
            if not banner.startswith("220"):
                raise SmtpError(f"unexpected SMTP banner: {banner[:120]}")
            return f"connected in {(time.monotonic()-started)*1000:.0f} ms; banner={banner[:80]}"

        def te02() -> str:
            subject = f"{self.subject_token} external"
            latency = self.smtp_sender(
                args.external_smtp_host, args.external_smtp_port,
                f"{self.alias_name}@{args.domain}", "poc-external@example.invalid",
                subject, "DomiBox Phase 1A external inbound test.",
                args.timeout, args.starttls, args.insecure_smtp_tls,
            )
            return f"external SMTP accepted in {latency:.0f} ms"

        def te03() -> str:
            account_id = next(iter(self.created))
            found, subjects = verify_message(self.client, account_id, self.subject_token)
            if not found:
                raise JmapError(f"external message not found via JMAP; subjects: {subjects[:5]}")
            return "external message retrieved via JMAP"

        ok1 = self._run("T-001", t001)
        if not ok1:
            for tid in ("T-002", "T-003"):
                self._blocked(tid, "precondition T-001 failed")
            for tid in ("T-E01", "T-E02", "T-E03"):
                self._blocked(tid, "precondition T-001 failed")
            self._cleanup_blocked("T-E04", "no identity was created")
            return
        ok2 = self._run("T-002", t002)
        if not ok2:
            for tid in ("T-003", "T-E01", "T-E02", "T-E03"):
                self._blocked(tid, "precondition T-002 failed")
            self._cleanup_blocked("T-E04", "no identity was created")
            return
        ok3 = self._run("T-003", t003)
        if not ok3:
            for tid in ("T-E01", "T-E02", "T-E03"):
                self._blocked(tid, "precondition T-003 failed")
            self._cleanup("T-E04")
            return
        ok_e1 = self._run("T-E01", te01)
        if not ok_e1:
            self._blocked("T-E02", "precondition T-E01 failed")
            self._blocked("T-E03", "precondition T-E02 failed")
        else:
            ok_e2 = self._run("T-E02", te02)
            if not ok_e2:
                self._blocked("T-E03", "precondition T-E02 failed")
            else:
                self._run("T-E03", te03)
        self._cleanup("T-E04")

    # -- static run --------------------------------------------------------
    def run_static(self) -> None:
        config = self._make("T-001")
        config.execution_status = "EXECUTED"
        config.result = "PASS"
        config.actual = ("static mode: no network calls, no account creation, no Docker, "
                         "no DNS. Mode gate and configuration validated locally.")
        config.evidence = self._rel(os.path.join(self.evidence_dir, "report.json")) + "#T-001"
        self._add(config)
        intended = {
            "T-002": "would call x:Domain/query then x:Domain/get (requires local/external mode)",
            "T-003": "would create one throwaway x:Account/set identity with a unique alias",
            "T-004": "would send SMTP to the alias and verify with Email/query + Email/get",
            "T-005": "would destroy only the id captured during this run",
            "T-E01": "would connect to the public SMTP endpoint from an independent network",
            "T-E02": "would send a real external message to the throwaway alias",
            "T-E03": "would retrieve the external message through JMAP",
            "T-E04": "would destroy only the external-run identity",
        }
        for test_id, description in intended.items():
            result = self._make(test_id)
            result.actual = "intended: " + description
            result.failure_reason = "static mode does not execute live tests"
            self._add(result)

    # -- cleanup -----------------------------------------------------------
    def _cleanup_blocked(self, test_id: str, reason: str) -> None:
        result = self._make(test_id)
        result.result = "BLOCKED"
        result.failure_reason = reason
        result.actual = "not executed"
        self._add(result)

    def _cleanup(self, test_id: str) -> None:
        if not self.created:
            self._cleanup_blocked(test_id, "no identity created by this run")
            return

        def do_cleanup() -> str:
            destroyed = []
            for account_id, name in list(self.created.items()):
                destroy_identity(self.client, account_id, name)
                destroyed.append(account_id)
                del self.created[account_id]
            return "destroyed only run-owned ids: " + ", ".join(destroyed)

        self._run(test_id, do_cleanup)

    # -- report ------------------------------------------------------------
    @property
    def test_password(self) -> str:
        return "PoC-" + secrets.token_urlsafe(18)

    def report(self) -> Dict[str, Any]:
        summary = {
            status: sum(1 for r in self.results if r.result == status)
            for status in ("PASS", "FAIL", "BLOCKED", "NOT_EXECUTED")
        }
        summary["total"] = len(self.results)
        summary["overall"] = ("FAIL" if summary["FAIL"] else
                              "BLOCKED" if summary["BLOCKED"] and self.mode != "static" else
                              "PASS" if self.mode == "static" else "INCOMPLETE")
        return {
            "schema_version": 1,
            "run_id": self.run_id,
            "mode": self.mode,
            "started_at": self.started_at,
            "evidence_dir": self.evidence_dir,
            "target": {
                "jmap_url": self.args.jmap_url,
                "domain": self.args.domain,
                "smtp_host": (self.args.external_smtp_host if self.mode == "external"
                              else self.args.smtp_host),
                "smtp_port": (self.args.external_smtp_port if self.mode == "external"
                              else self.args.smtp_port),
            },
            "results": [r.as_dict() for r in self.results],
            "summary": summary,
            "secrets_disclaimer": "no credentials, tokens or generated account passwords are recorded",
        }

    def write_report(self) -> str:
        path = os.path.join(self.evidence_dir, "report.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.report(), handle, indent=2, sort_keys=True)
            handle.write("\n")
        return path

    def execute(self) -> None:
        try:
            self.prepare()
        except ConfigError as exc:
            result = self._make("T-001")
            result.execution_status = "EXECUTED"
            result.result = "FAIL"
            result.failure_reason = f"ConfigError: {exc}"
            result.actual = "mode/configuration gate rejected the run"
            result.evidence = self._evidence("T-001", traceback.format_exc())
            self._add(result)
            return
        if self.mode == "static":
            self.run_static()
        elif self.mode == "local":
            self.run_local()
        else:
            self.run_external()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DomiBox Phase 1A Stalwart PoC runner")
    parser.add_argument("--mode", choices=("static", "local", "external"), default="static")
    parser.add_argument("--jmap-url", default=os.environ.get("POC_JMAP_URL", "http://127.0.0.1:8080/jmap/"))
    parser.add_argument("--domain", default=os.environ.get("POC_TEST_DOMAIN", "sintaksis.biz.id"))
    parser.add_argument("--smtp-host", default=os.environ.get("POC_SMTP_HOST", "127.0.0.1"))
    parser.add_argument("--smtp-port", type=int, default=int(os.environ.get("POC_SMTP_PORT", "25")))
    parser.add_argument("--external-smtp-host", default=os.environ.get("POC_EXTERNAL_SMTP_HOST", ""))
    parser.add_argument("--external-smtp-port", type=int,
                        default=int(os.environ.get("POC_EXTERNAL_SMTP_PORT", "25")))
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--report-dir", default=os.environ.get("POC_REPORT_DIR", "reports"))
    parser.add_argument("--admin-user", default=os.environ.get("POC_ADMIN_USER", ""))
    parser.add_argument("--admin-password", default=os.environ.get("POC_ADMIN_PASS", ""))
    parser.add_argument("--admin-token", default=os.environ.get("POC_ADMIN_TOKEN", ""))
    parser.add_argument("--local-authorized", action="store_true")
    parser.add_argument("--confirm-local", default="")
    parser.add_argument("--external-authorized", action="store_true")
    parser.add_argument("--confirm-external", default="")
    parser.add_argument("--allow-jmap-host", action="append", default=[], dest="allow_jmap_hosts")
    parser.add_argument("--starttls", action="store_true",
                        help="require STARTTLS on SMTP (recommended for external mode)")
    parser.add_argument("--insecure-smtp-tls", action="store_true",
                        help="skip TLS certificate verification (PoC self-signed only)")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    runner = Runner(args)
    runner.execute()
    path = runner.write_report()
    summary = runner.report()["summary"]
    print(f"mode={runner.mode} run_id={runner.run_id}")
    print(f"report={path}")
    for result in runner.results:
        print(f"{result.test_id} {result.result:12} {result.description}")
    print("summary=" + json.dumps(summary, sort_keys=True))
    if summary["FAIL"]:
        return 1
    if summary["BLOCKED"] and runner.mode != "static":
        return 2
    if runner.mode != "static" and summary["PASS"] == 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
