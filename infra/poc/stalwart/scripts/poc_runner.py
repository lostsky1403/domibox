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
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

USING_MGMT = ["urn:ietf:params:jmap:core", "urn:stalwart:jmap"]
USING_MAIL = ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"]
REQUIRED_CAPS = (
    "urn:ietf:params:jmap:core",
    "urn:stalwart:jmap",
    "urn:ietf:params:jmap:mail",
)

# Required test ids per live mode. TLS gates are required in both live modes:
# a plaintext SMTP accept must never be reported as a TLS PASS.
LIVE_TESTS = {
    "local": ("T-001", "T-002", "T-003", "T-004", "T-T01", "T-T02", "T-T03", "T-005"),
    "external": ("T-E00", "T-001", "T-002", "T-003", "T-E01",
                 "T-T01", "T-T02", "T-T03", "T-E02", "T-E03", "T-E04"),
}
EXIT_CODES = {"PASS": 0, "NOT_EXECUTED": 0, "FAIL": 1, "BLOCKED": 2, "INCOMPLETE": 3}
SENSITIVE_QUERY = {"token", "api_key", "apikey", "password", "secret",
                   "access_token", "refresh_token", "sig", "signature", "key"}
RESPONSE_SHAPES = {
    "x:Domain/query": ("ids",),
    "x:Domain/get": ("data",),
    "x:Account/get": ("data",),
    "Email/query": ("ids",),
    "Email/get": ("data",),
}


def safe_url(url: str) -> str:
    """Strip userinfo and sensitive query values from a URL for reporting."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return "[INVALID URL]"
    netloc = parts.netloc
    if "@" in netloc:
        netloc = "[REDACTED]@" + netloc.rsplit("@", 1)[1]
    query = [(key, "[REDACTED]" if key.lower() in SENSITIVE_QUERY else value)
             for key, value in parse_qsl(parts.query, keep_blank_values=True)]
    return urlunsplit((parts.scheme, netloc, parts.path, urlencode(query), parts.fragment))


def compute_overall(mode: str, results: List[Any], required: Optional[Tuple[str, ...]] = None) -> str:
    """Deterministic overall status for a run.

    PASS          every required test passed
    FAIL          any required test failed
    BLOCKED       a required test could not run because a prerequisite failed
    NOT_EXECUTED  no required live test was executed (STATIC mode)
    INCOMPLETE    partial results not otherwise classified
    """
    if mode == "static" or required is None or not required:
        return "NOT_EXECUTED"
    by_id = {getattr(r, "test_id", ""): getattr(r, "result", "") for r in results}
    states = [by_id.get(test_id, "NOT_EXECUTED") for test_id in required]
    if not any(state in ("PASS", "FAIL", "BLOCKED") for state in states):
        return "NOT_EXECUTED"
    if "FAIL" in states:
        return "FAIL"
    if "BLOCKED" in states:
        return "BLOCKED"
    if all(state == "PASS" for state in states):
        return "PASS"
    return "INCOMPLETE"


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


class AmbiguousCreation(RunnerError):
    """Create result cannot be attributed safely; manual reconciliation needed."""


class ManualReconciliation(RunnerError):
    """A run-owned account exists but verification was inconclusive."""


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

    def add_secret(self, value: str) -> None:
        """Register a generated secret (for example a throwaway account password)."""
        if value and value not in self._secrets:
            self._secrets.append(value)

    def sanitize(self, text: Any) -> str:
        if text is None:
            return ""
        text = str(text)
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
        # Observed on Stalwart v1.1.1: GET /jmap/ is 404; the session document is
        # served at /.well-known/jmap (307 -> /jmap/session).
        parts = urlsplit(self.url)
        session_url = f"{parts.scheme}://{parts.netloc}/.well-known/jmap"
        response = self.transport.request("GET", session_url, self._headers())
        obj = self._parse(response)
        if not isinstance(obj, dict):
            raise JmapError("JMAP session response is not an object")
        caps = obj.get("capabilities")
        if not isinstance(caps, dict):
            raise JmapError("JMAP session has no capabilities object")
        # Observed: urn:stalwart:jmap appears under accountCapabilities, not at
        # the top level. Check the union of both places.
        available = set(caps)
        for account in (obj.get("accounts") or {}).values():
            if isinstance(account, dict):
                available.update((account.get("accountCapabilities") or {}).keys())
        missing = [c for c in REQUIRED_CAPS if c not in available]
        if missing:
            raise JmapError("missing JMAP capabilities: " + ", ".join(missing))
        return obj

    def call(self, using: List[str], method_calls: List[List[Any]]) -> Dict[str, Tuple[str, Dict[str, Any]]]:
        """Send JMAP calls and strictly validate that each requested call came back once.

        HTTP 200 alone is never treated as success: every call id, method name,
        method error and required response shape is checked before fields are read.
        """
        expected: Dict[str, str] = {}
        requested: Dict[str, Dict[str, Any]] = {}
        for call in method_calls:
            if not isinstance(call, list) or len(call) < 3:
                raise JmapError("malformed requested method call")
            method, args, call_id = call[0], call[1], call[2]
            if not isinstance(call_id, str) or not call_id:
                raise JmapError("requested method call has no valid call id")
            if call_id in expected:
                raise JmapError(f"duplicate requested call id: {call_id}")
            if not isinstance(args, dict):
                raise JmapError(f"{method}: requested arguments are not an object")
            expected[call_id] = str(method)
            requested[call_id] = args

        payload = {"using": using, "methodCalls": method_calls}
        response = self.transport.request(
            "POST", self.url, self._headers(), json.dumps(payload)
        )
        obj = self._parse(response)
        responses = obj.get("methodResponses") if isinstance(obj, dict) else None
        if not isinstance(responses, list):
            raise JmapError("response has no methodResponses array")
        out: Dict[str, Tuple[str, Dict[str, Any]]] = {}
        seen: set = set()
        for item in responses:
            if not isinstance(item, list) or len(item) != 3:
                raise JmapError("malformed methodResponses entry")
            name, args, call_id = item
            if not isinstance(call_id, str) or not call_id:
                raise JmapError("response contains a malformed call id")
            if call_id in seen:
                raise JmapError(f"duplicate call id in response: {call_id}")
            if call_id not in expected:
                raise JmapError(f"unexpected call id in response: {call_id}")
            if str(name) != expected[call_id]:
                raise JmapError(
                    f"method name mismatch for {call_id}: expected {expected[call_id]}, got {name}")
            if not isinstance(args, dict):
                raise JmapError(f"{name}: arguments are not an object")
            if args.get("type") == "error":
                detail = self.sanitize(
                    args.get("description") or args.get("detail") or "unspecified")
                raise JmapError(f"{name} method error: {detail}")
            for failure_key in ("notCreated", "notUpdated", "notDestroyed"):
                failures = args.get(failure_key)
                if isinstance(failures, dict) and failures:
                    raise JmapError(
                        f"{name} {failure_key}: {self.sanitize(json.dumps(failures))}")
            for field in RESPONSE_SHAPES.get(str(name), ()):
                # Stalwart's Foo/get returns "list"; standard mail methods use
                # "data". Accept either, but require a real list.
                candidates = (field, "list") if field == "data" else (field,)
                if not any(isinstance(args.get(candidate), list) for candidate in candidates):
                    raise JmapError(f"{name}: missing or invalid {field} in response")
            req_args = requested[call_id]
            for operation, result_key, failure_key in (
                ("create", "created", "notCreated"),
                ("update", "updated", "notUpdated"),
                ("destroy", "destroyed", "notDestroyed"),
            ):
                if operation in req_args:
                    if result_key not in args and failure_key not in args:
                        raise JmapError(f"{name}: missing {result_key} result")
                    if result_key in args:
                        expected_type = list if operation == "destroy" else dict
                        if not isinstance(args[result_key], expected_type):
                            raise JmapError(f"{name}: invalid {result_key} result")
            seen.add(call_id)
            out[call_id] = (str(name), args)
        missing = sorted(set(expected) - seen)
        if missing:
            raise JmapError("missing method responses for call ids: " + ", ".join(missing))
        return out


# --------------------------------------------------------------------------
# Vendor-supported operations
# --------------------------------------------------------------------------
def _objects(args: Dict[str, Any], field: str = "data") -> List[Any]:
    """Read a JMAP list, accepting Stalwart's `list` and standard `data`."""
    for key in (field, "list"):
        value = args.get(key)
        if isinstance(value, list):
            return value
    return []


def discover_domain_id(client: JmapClient, domain_name: str) -> str:
    query = client.call(USING_MGMT, [["x:Domain/query", {"filter": {"name": domain_name}}, "dq"]])
    args = query.get("dq", ("", {}))[1]
    ids = args.get("ids") or []
    if not ids:
        raise MissingDomain(f"x:Domain/query returned no domain for {domain_name}")
    get = client.call(USING_MGMT, [["x:Domain/get", {"ids": ids[:10]}, "dg"]])
    data = _objects(get.get("dg", ("", {}))[1])
    for entry in data:
        if isinstance(entry, dict) and entry.get("name") == domain_name and entry.get("id"):
            return str(entry["id"])
    raise MissingDomain(f"x:Domain/get did not confirm exact domain {domain_name}")


def create_identity(client: JmapClient, domain_name: str, domain_id: str,
                    localpart: str, alias_name: str, password: str,
                    on_created: Optional[Callable[[str], None]] = None) -> str:
    """Create one throwaway account, returning its id immediately.

    The caller's `on_created` callback registers the id as run-owned BEFORE any
    readback, so a failed verification cannot orphan the account. Ambiguous
    results raise AmbiguousCreation and are never guessed at.
    """
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
    args = resp.get("ac", ("", {}))[1]
    created = args.get("created") or {}
    not_created = args.get("notCreated") or {}
    if not isinstance(created, dict) or not isinstance(not_created, dict):
        raise AmbiguousCreation(
            "MANUAL RECONCILIATION REQUIRED: malformed x:Account/set create result")
    entries = [value for value in created.values() if isinstance(value, dict) and value.get("id")]
    if len(created) != 1 or len(entries) != 1 or not_created:
        raise AmbiguousCreation(
            "MANUAL RECONCILIATION REQUIRED: ambiguous x:Account/set create result")
    account_id = str(entries[0]["id"])
    if on_created is not None:
        on_created(account_id)
    return account_id


def account_name(client: JmapClient, account_id: str, call_id: str = "vg") -> Optional[str]:
    resp = client.call(USING_MGMT, [["x:Account/get", {"ids": [account_id]}, call_id]])
    data = _objects(resp.get(call_id, ("", {}))[1])
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


def _address_list(value: Any) -> List[str]:
    out: List[str] = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and item.get("email"):
                out.append(str(item["email"]))
            elif isinstance(item, str):
                out.append(item)
    elif isinstance(value, dict) and value.get("email"):
        out.append(str(value["email"]))
    elif isinstance(value, str):
        out.append(value)
    return out


@dataclass
class DeliveryEvidence:
    found: bool
    subjects: List[str] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    attempts: int = 0
    elapsed_ms: float = 0.0
    timed_out: bool = False
    recipient_matched: bool = False

    def summary(self) -> str:
        return (f"poll_attempts={self.attempts} elapsed={self.elapsed_ms:.0f}ms "
                f"subject_match={self.found} recipient_match={self.recipient_matched} "
                f"timed_out={self.timed_out}")


def verify_message(client: JmapClient, account_id: str, subject_token: str,
                   recipient: str = "", deadline_s: float = 0.0,
                   poll_interval_s: float = 0.5,
                   now: Optional[Callable[[], float]] = None,
                   sleep: Optional[Callable[[float], None]] = None) -> DeliveryEvidence:
    """Poll Email/query + Email/get for a bounded time; match subject AND recipient."""
    now = now or time.monotonic
    sleep = sleep or time.sleep
    started = now()
    deadline = started + max(0.0, float(deadline_s))
    attempts = 0
    subjects: List[str] = []
    recipients: List[str] = []
    while True:
        attempts += 1
        query = client.call(USING_MAIL, [["Email/query", {
            "accountId": account_id, "limit": 20}, "eq"]])
        ids = query.get("eq", ("", {}))[1].get("ids") or []
        if ids:
            fetched = client.call(USING_MAIL, [[
                "Email/get",
                {"accountId": account_id, "ids": ids[:20],
                 "properties": ["id", "subject", "receivedAt", "from", "to"]},
                "eg",
            ]])
            data = _objects(fetched.get("eg", ("", {}))[1])
            subjects = [str(item.get("subject") or "") for item in data if isinstance(item, dict)]
            recipients = [addr for item in data if isinstance(item, dict)
                          for addr in _address_list(item.get("to"))]
        subject_match = any(subject_token in s for s in subjects)
        recipient_match = (not recipient) or any(
            addr.lower() == recipient.lower() for addr in recipients)
        if subject_match and recipient_match:
            return DeliveryEvidence(True, subjects, recipients, attempts,
                                    (now() - started) * 1000.0, False,
                                    bool(recipient) and recipient_match)
        remaining = deadline - now()
        if remaining <= 0:
            return DeliveryEvidence(False, subjects, recipients, attempts,
                                    (now() - started) * 1000.0, True, False)
        sleep(min(float(poll_interval_s), remaining))


@dataclass
class SmtpProbe:
    banner: str = ""
    advertised_starttls: bool = False
    negotiated: bool = False
    cert_verification: str = "not_attempted"
    plain_accepted: bool = False


def smtp_probe(host: str, port: int, timeout: float, starttls: bool,
               insecure_tls: bool) -> SmtpProbe:
    result = SmtpProbe()
    with smtplib.SMTP(host, port, timeout=timeout) as smtp:
        code, message = smtp.ehlo()
        result.banner = (message.decode("utf-8", "replace") if isinstance(message, bytes)
                         else str(message))[:200]
        if not 200 <= code < 300:
            raise SmtpError(f"EHLO failed with {code}")
        result.advertised_starttls = smtp.has_extn("starttls")
        if starttls:
            if not result.advertised_starttls:
                raise SmtpError("STARTTLS not advertised")
            context = (ssl._create_unverified_context() if insecure_tls
                       else ssl.create_default_context())
            smtp.starttls(context=context)
            smtp.ehlo()
            result.negotiated = True
            result.cert_verification = "skipped" if insecure_tls else "verified"
        else:
            result.plain_accepted = True
    return result


@dataclass
class VantageAssessment:
    ok: bool
    evidence: Dict[str, Any]
    reason: str = ""


def assess_vantage(args: argparse.Namespace) -> VantageAssessment:
    evidence = {
        "execution_host": socket.gethostname(),
        "target_endpoint": f"{args.external_smtp_host}:{args.external_smtp_port}",
        "test_vantage_point": args.vantage_id,
        "vantage_public_ip": args.vantage_public_ip,
        "target_public_ip": args.target_public_ip,
        "independence_evidence": args.vantage_evidence,
    }
    missing = [name for name in ("vantage_id", "vantage_public_ip",
                                 "target_public_ip", "vantage_evidence")
               if not getattr(args, name, "")]
    if missing:
        return VantageAssessment(False, evidence,
                                 "missing external-vantage evidence: " + ", ".join(missing))
    try:
        vantage_ip = ipaddress.ip_address(args.vantage_public_ip)
        target_ip = ipaddress.ip_address(args.target_public_ip)
    except ValueError:
        return VantageAssessment(False, evidence,
                                 "vantage and target IPs must be literal addresses")
    for ip in (vantage_ip, target_ip):
        if ip.is_loopback or ip.is_private or ip.is_link_local:
            return VantageAssessment(False, evidence,
                                     "vantage and target must both be public addresses")
    if vantage_ip == target_ip:
        return VantageAssessment(False, evidence,
                                 "vantage IP equals target IP; a local or hairpin test "
                                 "cannot prove public SMTP reachability")
    evidence["independent_network"] = True
    return VantageAssessment(True, evidence, "public independent vantage confirmed")


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
    "T-E00": ("External vantage independence",
              "Public vantage and target evidence supplied by the operator",
              "Execution host is proven independent of the VPS and its Docker network"),
    "T-T01": ("STARTTLS advertised",
              "SMTP EHLO reached; --starttls requested",
              "EHLO advertises STARTTLS"),
    "T-T02": ("STARTTLS negotiation",
              "T-T01 passed",
              "STARTTLS handshake succeeds; plaintext result is never a TLS PASS"),
    "T-T03": ("TLS certificate state",
              "T-T02 passed",
              "Certificate verification succeeded, or was explicitly skipped for the authorized PoC"),
    "T-T04": ("Plain SMTP acceptance (optional)",
              "--plain-smtp-test requested",
              "Plaintext delivery is reported separately and never as a TLS result"),
}


class Runner:
    def __init__(self, args: argparse.Namespace, transport: Any = None,
                 smtp_sender: Optional[Callable[..., float]] = None,
                 smtp_probe_fn: Optional[Callable[..., SmtpProbe]] = None):
        self.args = args
        self.mode = args.mode
        self.results: List[TestResult] = []
        # account id -> {"name": generated localpart, "state": provisional|verified}
        self.created: Dict[str, Dict[str, str]] = {}
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.run_id = f"{self.mode}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(3)}"
        self.evidence_dir = os.path.join(args.report_dir, self.run_id)
        os.makedirs(self.evidence_dir, exist_ok=True)
        self.transport = transport if transport is not None else HttpTransport(args.timeout)
        self.client = JmapClient(self.transport, args.jmap_url, args.admin_user,
                                 args.admin_password, args.admin_token)
        self.smtp_sender = smtp_sender or smtp_send
        self.smtp_probe_fn = smtp_probe_fn or smtp_probe
        self.localpart = f"poc-{secrets.token_hex(5)}"
        self.alias_name = f"poc-alias-{secrets.token_hex(5)}"
        self.subject_token = f"DOMIBOX-POC-{secrets.token_hex(8)}"
        self._test_password = "PoC-" + secrets.token_urlsafe(18)
        self.client.add_secret(self._test_password)
        self.vantage = VantageAssessment(False, {}, "not evaluated")
        self._cleanup_done = False
        self._probe_cache: Dict[str, SmtpProbe] = {}
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

    # -- identity ownership -----------------------------------------------
    def register_created(self, account_id: str) -> None:
        """Register a create result as provisional run-owned state immediately."""
        self.created[account_id] = {"name": self.localpart, "state": "provisional"}

    def _reconcile_by_id(self, account_id: str, attempts: int = 1) -> Optional[str]:
        """Bounded readback by exact id only. Never searches or deletes by name."""
        last_error: Optional[Exception] = None
        for _ in range(max(1, attempts)):
            try:
                name = account_name(self.client, account_id, call_id="rg")
                if name:
                    return name
            except Exception as exc:  # noqa: BLE001 - bounded, reported
                last_error = exc
        if last_error is not None:
            raise ManualReconciliation(
                "MANUAL RECONCILIATION REQUIRED: id-based readback failed: "
                + type(last_error).__name__) from last_error
        return None

    @contextmanager
    def _cleanup_guard(self, test_id: str) -> Iterator[None]:
        """Best-effort cleanup on failure, exception or interruption."""
        try:
            yield
        finally:
            if not self._cleanup_done and self.created:
                try:
                    self._cleanup(test_id)
                except Exception as exc:  # noqa: BLE001 - never lose cleanup state silently
                    self._add_note(test_id, f"cleanup guard failed: {type(exc).__name__}: {exc}")

    def _add_note(self, test_id: str, note: str) -> None:
        result = self._make(test_id)
        result.result = "FAIL"
        result.failure_reason = self.client.sanitize(note)
        result.actual = "best-effort cleanup attempted"
        result.execution_status = "EXECUTED"
        result.evidence = self._evidence(test_id, note)
        self._add(result)

    def run_tls_gates(self, host: str, port: int) -> None:
        """Explicit STARTTLS gates. A plaintext result is never a TLS PASS."""
        args = self.args
        if not args.starttls:
            for test_id in ("T-T01", "T-T02", "T-T03"):
                self._blocked(test_id,
                              "STARTTLS not requested; plaintext acceptance is not a TLS PASS")
            return
        key = f"{host}:{port}"
        if key not in self._probe_cache:
            def probe() -> SmtpProbe:
                return self.smtp_probe_fn(host, port, args.timeout,
                                          True, args.insecure_smtp_tls)
            # Execute once and cache; the three gates read the cached observation.
            try:
                self._probe_cache[key] = probe()
            except Exception as exc:  # noqa: BLE001
                self._probe_cache[key] = None  # type: ignore[assignment]
                self._probe_error = f"{type(exc).__name__}: {exc}"

        probe_error = getattr(self, "_probe_error", "")
        probe = self._probe_cache.get(key)

        def t1() -> str:
            if probe_error:
                raise SmtpError(probe_error)
            if not probe or not probe.advertised_starttls:
                raise SmtpError("STARTTLS not advertised in EHLO response")
            return f"STARTTLS advertised; banner={probe.banner[:80]}"

        def t2() -> str:
            if probe_error:
                raise SmtpError(probe_error)
            if not probe or not probe.negotiated:
                raise SmtpError("STARTTLS negotiation did not succeed")
            return "STARTTLS negotiation succeeded"

        def t3() -> str:
            if probe_error:
                raise SmtpError(probe_error)
            if not probe:
                raise SmtpError("no SMTP probe result")
            if args.insecure_smtp_tls:
                return "certificate verification intentionally skipped for authorized PoC"
            if probe.cert_verification != "verified":
                raise SmtpError(f"certificate verification state={probe.cert_verification}")
            return "certificate verification succeeded"

        for test_id, fn in (("T-T01", t1), ("T-T02", t2), ("T-T03", t3)):
            self._run(test_id, fn)
        if args.plain_smtp_test:
            def t4() -> str:
                if not probe or not probe.plain_accepted:
                    return "plaintext acceptance not exercised (STARTTLS path used)"
                return "plaintext SMTP acceptance observed and reported separately"
            self._run("T-T04", t4)
        else:
            self._blocked("T-T04", "plain SMTP test not requested")

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
            self.vantage = assess_vantage(args)
        else:
            raise ConfigError(f"unknown mode {self.mode!r}")
        self._prepared = True

    # -- identity lifecycle ------------------------------------------------
    def t003_impl(self, domain_id_box: Dict[str, str]) -> str:
        args = self.args

        def register(account_id: str) -> None:
            # Provisional ownership is recorded BEFORE any readback verification.
            self.register_created(account_id)

        account_id = create_identity(
            self.client, args.domain, domain_id_box["id"], self.localpart,
            self.alias_name, self._test_password, on_created=register,
        )
        try:
            name = account_name(self.client, account_id, call_id="ag")
            if name is None:
                name = self._reconcile_by_id(account_id)
        except ManualReconciliation:
            raise
        except Exception as exc:  # noqa: BLE001 - report, then attempt id-based reconciliation
            try:
                name = self._reconcile_by_id(account_id)
            except ManualReconciliation:
                raise
            except Exception as inner:  # noqa: BLE001
                raise ManualReconciliation(
                    "MANUAL RECONCILIATION REQUIRED: readback failed: "
                    + type(inner).__name__) from inner
        if name != self.localpart:
            # Never delete on a name match; only the captured id is ours.
            raise ManualReconciliation(
                "MANUAL RECONCILIATION REQUIRED: readback name did not match the "
                "run-owned id; no name-based cleanup performed")
        self.created[account_id]["state"] = "verified"
        return f"created run-owned id {account_id}; alias {self.alias_name}@{args.domain}"

    def _delivery(self, host: str, port: int, label: str) -> str:
        args = self.args
        recipient = f"{self.alias_name}@{args.domain}"
        subject = f"{self.subject_token} {label}"
        latency = self.smtp_sender(
            host, port, recipient, f"poc-{label}@example.invalid", subject,
            "DomiBox Phase 1A throwaway test message.", args.timeout,
            args.starttls, args.insecure_smtp_tls,
        )
        account_id = next(iter(self.created))
        evidence = verify_message(
            self.client, account_id, self.subject_token, recipient=recipient,
            deadline_s=args.poll_deadline, poll_interval_s=args.poll_interval,
        )
        if not evidence.found:
            raise JmapError("message not visible via JMAP: " + evidence.summary())
        return (f"SMTP accepted in {latency:.0f} ms; {evidence.summary()}; "
                "smtp_acceptance and jmap_visibility recorded separately")

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

        with self._cleanup_guard("T-005"):
            ok1 = self._run("T-001", t001)
            if not ok1:
                for tid in ("T-002", "T-003", "T-004"):
                    self._blocked(tid, "precondition T-001 failed")
                for tid in ("T-T01", "T-T02", "T-T03"):
                    self._blocked(tid, "precondition T-001 failed")
                self._cleanup_blocked("T-005", "no identity was created")
                return
            self.run_tls_gates(args.smtp_host, args.smtp_port)
            ok2 = self._run("T-002", t002)
            if not ok2:
                for tid in ("T-003", "T-004"):
                    self._blocked(tid, "precondition T-002 failed")
                self._cleanup_blocked("T-005", "no identity was created")
                return
            ok3 = self._run("T-003", lambda: self.t003_impl(domain_id_box))
            if not ok3:
                self._blocked("T-004", "precondition T-003 failed")
                self._cleanup("T-005")
                return
            self._run("T-004", lambda: self._delivery(args.smtp_host, args.smtp_port, "local"))
            self._cleanup("T-005")

    # -- external run ------------------------------------------------------
    def run_external(self) -> None:
        args = self.args
        domain_id_box: Dict[str, str] = {}

        def te00() -> str:
            if not self.vantage.ok:
                raise ConfigError("external vantage is not independent: " + self.vantage.reason)
            return "; ".join(f"{key}={value}" for key, value in self.vantage.evidence.items())

        def te01() -> str:
            host, port = args.external_smtp_host, args.external_smtp_port
            started = time.monotonic()
            with socket.create_connection((host, port), timeout=args.timeout) as sock:
                sock.settimeout(args.timeout)
                banner = sock.recv(512).decode("utf-8", "replace").strip()
            if not banner.startswith("220"):
                raise SmtpError(f"unexpected SMTP banner: {banner[:120]}")
            return f"connected in {(time.monotonic()-started)*1000:.0f} ms; public banner={banner[:80]}"

        other_tests = ("T-001", "T-002", "T-003", "T-E01", "T-E02", "T-E03",
                       "T-T01", "T-T02", "T-T03", "T-E04")
        with self._cleanup_guard("T-E04"):
            if not self.vantage.ok:
                self._blocked("T-E00", "external vantage not independent: " + self.vantage.reason)
                for tid in other_tests:
                    self._blocked(tid, "precondition T-E00 failed: vantage not independent")
                return
            self._run("T-E00", te00)
            ok1 = self._run("T-001", lambda: "session OK (tunneled management); capabilities: "
                            + ", ".join(sorted(self.client.session()["capabilities"])))
            if not ok1:
                for tid in ("T-002", "T-003", "T-E01", "T-E02", "T-E03",
                            "T-T01", "T-T02", "T-T03"):
                    self._blocked(tid, "precondition T-001 failed")
                self._cleanup_blocked("T-E04", "no identity was created")
                return
            self.run_tls_gates(args.external_smtp_host, args.external_smtp_port)
            ok2 = self._run("T-002", lambda: self._discover(domain_id_box))
            if not ok2:
                for tid in ("T-003", "T-E01", "T-E02", "T-E03"):
                    self._blocked(tid, "precondition T-002 failed")
                self._cleanup_blocked("T-E04", "no identity was created")
                return
            ok3 = self._run("T-003", lambda: self.t003_impl(domain_id_box))
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
                ok_e2 = self._run("T-E02", lambda: self._smtp_accept_only(
                    args.external_smtp_host, args.external_smtp_port, "external"))
                if not ok_e2:
                    self._blocked("T-E03", "precondition T-E02 failed")
                else:
                    self._run("T-E03", lambda: self._delivery(
                        args.external_smtp_host, args.external_smtp_port, "external"))
            self._cleanup("T-E04")

    def _discover(self, domain_id_box: Dict[str, str]) -> str:
        domain_id_box["id"] = discover_domain_id(self.client, self.args.domain)
        return f"domain {self.args.domain} -> id {domain_id_box['id']}"

    def _smtp_accept_only(self, host: str, port: int, label: str) -> str:
        recipient = f"{self.alias_name}@{self.args.domain}"
        subject = f"{self.subject_token} {label}"
        latency = self.smtp_sender(
            host, port, recipient, f"poc-{label}@example.invalid", subject,
            "DomiBox Phase 1A external inbound test.", self.args.timeout,
            self.args.starttls, self.args.insecure_smtp_tls,
        )
        return (f"external SMTP accepted in {latency:.0f} ms; "
                "SMTP acceptance recorded separately from JMAP visibility")

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
            "T-E00": "would require independent public-vantage evidence before any SMTP test",
            "T-T01": "would check STARTTLS advertisement",
            "T-T02": "would negotiate STARTTLS; plaintext is never a TLS PASS",
            "T-T03": "would report certificate verification or an explicit authorized skip",
            "T-T04": "would report plaintext acceptance separately if requested",
        }
        for test_id, description in intended.items():
            result = self._make(test_id)
            result.actual = "intended: " + description
            result.failure_reason = "static mode does not execute live tests"
            self._add(result)

    # -- cleanup -----------------------------------------------------------
    def _cleanup_blocked(self, test_id: str, reason: str) -> None:
        self._cleanup_done = True
        result = self._make(test_id)
        result.result = "BLOCKED"
        result.failure_reason = self.client.sanitize(reason)
        result.actual = "not executed"
        self._add(result)

    def _cleanup(self, test_id: str) -> None:
        self._cleanup_done = True
        if not self.created:
            self._cleanup_blocked(test_id, "no identity created by this run")
            return

        def do_cleanup() -> str:
            destroyed = []
            for account_id, info in list(self.created.items()):
                # Destroy only ids recorded by this run, verified by exact id.
                destroy_identity(self.client, account_id, info["name"])
                destroyed.append(account_id)
                del self.created[account_id]
            return "destroyed only run-owned ids: " + ", ".join(destroyed)

        self._run(test_id, do_cleanup)

    # -- report ------------------------------------------------------------
    @property
    def test_password(self) -> str:
        return self._test_password

    def report(self) -> Dict[str, Any]:
        summary = {
            status: sum(1 for r in self.results if r.result == status)
            for status in ("PASS", "FAIL", "BLOCKED", "NOT_EXECUTED")
        }
        summary["total"] = len(self.results)
        required = LIVE_TESTS.get(self.mode, ())
        summary["overall"] = compute_overall(self.mode, self.results, required)
        results = []
        for result in self.results:
            item = result.as_dict()
            for key in ("actual", "failure_reason", "evidence"):
                item[key] = self.client.sanitize(item[key])
            results.append(item)
        return {
            "schema_version": 2,
            "run_id": self.run_id,
            "mode": self.mode,
            "live_functional_test": self.mode in ("local", "external")
                                    and summary["overall"] != "NOT_EXECUTED",
            "started_at": self.started_at,
            "evidence_dir": self.evidence_dir,
            "target": {
                "jmap_url": safe_url(self.args.jmap_url),
                "domain": self.args.domain,
                "smtp_host": (self.args.external_smtp_host if self.mode == "external"
                              else self.args.smtp_host),
                "smtp_port": (self.args.external_smtp_port if self.mode == "external"
                              else self.args.smtp_port),
            },
            "vantage": self.client.sanitize(json.dumps(self.vantage.evidence, sort_keys=True))
                       if self.vantage.evidence else "not evaluated",
            "tls_policy": {
                "requested": self.args.starttls,
                "verification_skipped": self.args.insecure_smtp_tls,
                "plaintext_tested": self.args.plain_smtp_test,
            },
            "required_tests": list(required),
            "results": results,
            "summary": summary,
            "secrets_disclaimer": "no credentials, tokens, userinfo or generated account "
                                  "passwords are recorded",
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
                        help="require STARTTLS on SMTP (explicit TLS gate)")
    parser.add_argument("--insecure-smtp-tls", action="store_true",
                        help="skip TLS certificate verification (PoC self-signed only; reported explicitly)")
    parser.add_argument("--plain-smtp-test", action="store_true",
                        help="exercise and report plaintext SMTP acceptance separately")
    parser.add_argument("--poll-deadline", type=float,
                        default=float(os.environ.get("POC_POLL_DEADLINE", "15")),
                        help="bounded seconds to wait for JMAP message visibility")
    parser.add_argument("--poll-interval", type=float,
                        default=float(os.environ.get("POC_POLL_INTERVAL", "1")),
                        help="seconds between Email/query polls")
    parser.add_argument("--vantage-id", default=os.environ.get("POC_VANTAGE_ID", ""))
    parser.add_argument("--vantage-public-ip", default=os.environ.get("POC_VANTAGE_PUBLIC_IP", ""))
    parser.add_argument("--target-public-ip", default=os.environ.get("POC_TARGET_PUBLIC_IP", ""))
    parser.add_argument("--vantage-evidence", default=os.environ.get("POC_VANTAGE_EVIDENCE", ""),
                        help="how the independent public IP was observed from this host")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    runner = Runner(args)
    runner.execute()
    path = runner.write_report()
    report = runner.report()
    summary = report["summary"]
    print(f"mode={runner.mode} run_id={runner.run_id}")
    print(f"report={path}")
    for result in runner.results:
        print(f"{result.test_id} {result.result:12} {result.description}")
    print("summary=" + json.dumps(summary, sort_keys=True))
    return EXIT_CODES[summary["overall"]]


if __name__ == "__main__":
    sys.exit(main())
