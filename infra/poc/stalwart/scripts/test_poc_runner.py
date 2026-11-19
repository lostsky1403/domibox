#!/usr/bin/env python3
"""Fail-closed mock tests for the DomiBox Phase 1A PoC runner.

No network, no Docker, no VPS, no images. Pure stdlib + injected transports.
Run:  python scripts/test_poc_runner.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poc_runner as pr  # noqa: E402

DOMAIN = "sintaksis.biz.id"
SECRET = "never-print-me"


class MockTransport:
    def __init__(self, responses, default_response=None):
        self.responses = list(responses)
        self.default_response = default_response
        self.calls = []

    def request(self, method, url, headers=None, body=None):
        self.calls.append({"method": method, "url": url, "body": body or ""})
        if not self.responses:
            if self.default_response is not None:
                if callable(self.default_response):
                    return self.default_response(body or "")
                return self.default_response
            raise AssertionError("unexpected extra request to mocked transport")
        return self.responses.pop(0)


def jmap(*entries):
    return pr.Response(200, json.dumps({
        "methodResponses": [[name, args, call_id] for name, args, call_id in entries],
        "sessionState": "mock-session",
    }))


def session_response():
    return pr.Response(200, json.dumps({
        "capabilities": {cap: {} for cap in pr.REQUIRED_CAPS},
        "accounts": {},
    }))


def ok_smtp(*_args, **_kwargs):
    return 12.0


def timeout_smtp(*_args, **_kwargs):
    raise pr.SmtpError("SMTP timeout")


def ok_probe(*_args, **_kwargs):
    return pr.SmtpProbe(banner="220 mock ESMTP", advertised_starttls=True,
                        negotiated=True, cert_verification="verified")


def no_starttls_probe(*_args, **_kwargs):
    return pr.SmtpProbe(banner="220 mock ESMTP", advertised_starttls=False)


def failing_tls_probe(*_args, **_kwargs):
    raise pr.SmtpError("STARTTLS negotiation failed")


def base_script(runner):
    """Vendor-shaped responses in the exact order the local runner calls them."""
    return [
        session_response(),
        jmap(("x:Domain/query", {"ids": ["d1"]}, "dq")),
        jmap(("x:Domain/get", {"data": [{"id": "d1", "name": DOMAIN}]}, "dg")),
        jmap(("x:Account/set", {"created": {"new1": {"id": "a1"}}}, "ac")),
        jmap(("x:Account/get", {"data": [{"id": "a1", "name": runner.localpart}]}, "ag")),
        jmap(("Email/query", {"ids": ["e1"]}, "eq")),
        jmap(("Email/get", {"data": [
            {"id": "e1", "subject": runner.subject_token + " local",
             "to": [{"email": f"{runner.alias_name}@{DOMAIN}"}]}]}, "eg")),
        jmap(("x:Account/get", {"data": [{"id": "a1", "name": runner.localpart}]}, "vg")),
        jmap(("x:Account/set", {"destroyed": ["a1"]}, "dd")),
    ]


class RunnerMockTests(unittest.TestCase):
    def _new_runner(self, smtp=ok_smtp, mode="local", extra=None, probe=None):
        tmp = tempfile.mkdtemp(prefix="domibox-poc-test-")
        argv = [
            "--mode", mode,
            "--report-dir", tmp,
            "--jmap-url", "http://127.0.0.1:8080/jmap/",
            "--domain", DOMAIN,
            "--admin-user", "poc-admin@example.invalid",
            "--admin-password", SECRET,
            "--poll-deadline", "0",
            "--poll-interval", "0",
        ]
        if mode == "local":
            argv += ["--local-authorized", "--confirm-local", "LOCAL-POC"]
        elif mode == "external":
            argv += ["--external-authorized"]
        if extra:
            argv += extra
        args = pr.build_parser().parse_args(argv)
        runner = pr.Runner(args, transport=MockTransport([]), smtp_sender=smtp,
                           smtp_probe_fn=probe)
        return runner

    def _run_case(self, script_builder=base_script, smtp=ok_smtp, extra=None,
                  mode="local", probe=None, default_response=None,
                  skip_secret_check=False):
        runner = self._new_runner(smtp=smtp, mode=mode, extra=extra, probe=probe)
        runner.transport = MockTransport(script_builder(runner), default_response)
        runner.client = pr.JmapClient(
            runner.transport, runner.args.jmap_url,
            runner.args.admin_user, runner.args.admin_password,
            runner.args.admin_token,
        )
        runner.client.add_secret(runner._test_password)
        runner.execute()
        report_path = runner.write_report()
        if not skip_secret_check:
            self.assert_no_secrets(runner, report_path)
        return runner

    def assert_no_secrets(self, runner, report_path):
        with open(report_path, "r", encoding="utf-8") as handle:
            content = handle.read()
        self.assertNotIn(SECRET, content)
        for name in os.listdir(runner.evidence_dir):
            with open(os.path.join(runner.evidence_dir, name), "r", encoding="utf-8") as handle:
                text = handle.read()
            self.assertNotIn(SECRET, text)

    def results(self, runner):
        return {r.test_id: r for r in runner.results}

    # -- required cases ----------------------------------------------------
    def test_01_successful_account_creation_and_full_flow(self):
        runner = self._run_case()
        results = self.results(runner)
        for test_id in ("T-001", "T-002", "T-003", "T-004", "T-005"):
            self.assertEqual(results[test_id].result, "PASS", test_id)
            self.assertEqual(results[test_id].execution_status, "EXECUTED", test_id)
        self.assertEqual(runner.report()["summary"]["FAIL"], 0)
        self.assertEqual(runner.created, {})

    def test_02_http_authorization_failure_does_not_pass(self):
        runner = self._run_case(lambda r: [pr.Response(401, "unauthorized")])
        results = self.results(runner)
        self.assertEqual(results["T-001"].result, "FAIL")
        self.assertIn("HTTP 401", results["T-001"].failure_reason)
        for test_id in ("T-002", "T-003", "T-004", "T-005"):
            self.assertEqual(results[test_id].result, "BLOCKED", test_id)
        self.assertNotIn("PASS", [x.result for x in runner.results])

    def test_03_invalid_jmap_method_error(self):
        def script(r):
            s = base_script(r)
            s[1] = jmap(("x:Domain/query", {
                "type": "error", "description": "unknown method"}, "dq"))
            return s
        results = self.results(self._run_case(script))
        self.assertEqual(results["T-002"].result, "FAIL")
        self.assertIn("unknown method", results["T-002"].failure_reason)

    def test_04_missing_domain(self):
        def script(r):
            s = base_script(r)
            s[1] = jmap(("x:Domain/query", {"ids": []}, "dq"))
            return s
        results = self.results(self._run_case(script))
        self.assertEqual(results["T-002"].result, "FAIL")
        self.assertEqual(results["T-003"].result, "BLOCKED")

    def test_05_account_creation_failure(self):
        def script(r):
            s = base_script(r)
            s[3] = jmap(("x:Account/set", {
                "notCreated": {"new1": {"type": "invalidProperties"}}}, "ac"))
            return s
        results = self.results(self._run_case(script))
        self.assertEqual(results["T-003"].result, "FAIL")
        self.assertEqual(results["T-004"].result, "BLOCKED")
        self.assertEqual(results["T-005"].result, "BLOCKED")

    def test_06_message_not_delivered(self):
        def script(r):
            s = base_script(r)
            s[5] = jmap(("Email/query", {"ids": []}, "eq"))
            return s[:6] + s[7:]  # Email/get never called when no ids are returned
        results = self.results(self._run_case(script))
        self.assertEqual(results["T-004"].result, "FAIL")
        self.assertIn("not visible via JMAP", results["T-004"].failure_reason)
        self.assertEqual(results["T-005"].result, "PASS")

    def test_07_smtp_timeout(self):
        def script(r):
            s = base_script(r)
            return s[:5] + s[7:]  # SMTP fails before Email/query
        results = self.results(self._run_case(script, smtp=timeout_smtp))
        self.assertEqual(results["T-004"].result, "FAIL")
        self.assertIn("SMTP timeout", results["T-004"].failure_reason)
        self.assertEqual(results["T-005"].result, "PASS")

    def test_08_cleanup_failure(self):
        def script(r):
            s = base_script(r)
            s[8] = jmap(("x:Account/set", {
                "notDestroyed": {"a1": {"type": "notFound"}}}, "dd"))
            return s
        results = self.results(self._run_case(script))
        self.assertEqual(results["T-005"].result, "FAIL")
        self.assertIn("notDestroyed", results["T-005"].failure_reason)

    def test_09_invalid_json_response(self):
        runner = self._run_case(lambda r: [pr.Response(200, "this is not json")])
        results = self.results(runner)
        self.assertEqual(results["T-001"].result, "FAIL")
        self.assertIn("valid JSON", results["T-001"].failure_reason)

    def test_10_missing_account_id(self):
        def script(r):
            s = base_script(r)
            s[3] = jmap(("x:Account/set", {"created": {"new1": {}}}, "ac"))
            return s
        results = self.results(self._run_case(script))
        self.assertEqual(results["T-003"].result, "FAIL")
        self.assertIn("MANUAL RECONCILIATION REQUIRED", results["T-003"].failure_reason)

    def test_11_refuses_to_delete_account_not_created_by_this_run(self):
        def script(r):
            s = base_script(r)
            s[7] = jmap(("x:Account/get", {
                "data": [{"id": "a1", "name": "unrelated-production-account"}]}, "vg"))
            return s
        runner = self._run_case(script)
        results = self.results(runner)
        self.assertEqual(results["T-005"].result, "FAIL")
        self.assertIn("not an identity created by this run", results["T-005"].failure_reason)
        bodies = [call["body"] for call in runner.transport.calls]
        self.assertFalse(any("destroy" in b for b in bodies),
                         "runner issued a destroy despite ownership guard failing")

    # -- mode gates --------------------------------------------------------
    def test_12_static_mode_makes_no_network_calls(self):
        runner = self._new_runner(mode="static")
        runner.transport = MockTransport([])
        runner.client = pr.JmapClient(runner.transport, runner.args.jmap_url, "", "")
        runner.execute()
        runner.write_report()
        self.assertEqual(runner.transport.calls, [])
        results = self.results(runner)
        self.assertEqual(results["T-001"].result, "PASS")
        for test_id in ("T-003", "T-004", "T-E01"):
            self.assertEqual(results[test_id].result, "NOT_EXECUTED", test_id)

    def test_13_local_mode_rejects_non_loopback_jmap(self):
        runner = self._new_runner(extra=["--jmap-url", "http://10.0.0.5:8080/jmap/",
                                        "--confirm-local", "LOCAL-POC"])
        runner.execute()
        self.assertEqual(self.results(runner)["T-001"].result, "FAIL")
        self.assertIn("loopback", self.results(runner)["T-001"].failure_reason)

    def test_14_external_mode_rejects_loopback_target(self):
        runner = self._new_runner(mode="external", extra=[
            "--external-smtp-host", "127.0.0.1",
            "--external-authorized", "--confirm-external", "127.0.0.1",
        ])
        runner.execute()
        self.assertEqual(self.results(runner)["T-001"].result, "FAIL")
        self.assertIn("public address", self.results(runner)["T-001"].failure_reason)


class _StatusResult:
    def __init__(self, test_id, result):
        self.test_id = test_id
        self.result = result


class RunnerHardeningTests(unittest.TestCase):
    # Reuse the harness helpers without re-running the original 14 test methods.
    _new_runner = RunnerMockTests._new_runner
    _run_case = RunnerMockTests._run_case
    assert_no_secrets = RunnerMockTests.assert_no_secrets
    results = RunnerMockTests.results

    # -- report correctness -----------------------------------------------
    def test_15_all_live_pass_reports_pass_not_incomplete(self):
        runner = self._run_case(extra=["--starttls"], probe=ok_probe)
        results = {r.test_id: r for r in runner.results}
        for test_id in pr.LIVE_TESTS["local"]:
            self.assertEqual(results[test_id].result, "PASS", test_id)
        report = runner.report()
        self.assertEqual(report["summary"]["overall"], "PASS")
        self.assertTrue(report["live_functional_test"])
        self.assertEqual(pr.EXIT_CODES["PASS"], 0)

    def test_16_overall_status_rules(self):
        required = ("A", "B")
        make = lambda pairs: [_StatusResult(k, v) for k, v in pairs]
        self.assertEqual(pr.compute_overall("local", make([("A", "PASS"), ("B", "PASS")]), required), "PASS")
        self.assertEqual(pr.compute_overall("local", make([("A", "FAIL"), ("B", "PASS")]), required), "FAIL")
        self.assertEqual(pr.compute_overall("local", make([("A", "BLOCKED"), ("B", "PASS")]), required), "BLOCKED")
        self.assertEqual(pr.compute_overall("local", make([("A", "NOT_EXECUTED"), ("B", "NOT_EXECUTED")]), required), "NOT_EXECUTED")
        self.assertEqual(pr.compute_overall("local", make([("A", "PASS"), ("B", "NOT_EXECUTED")]), required), "INCOMPLETE")
        self.assertEqual(pr.compute_overall("static", make([("A", "PASS")]), ()), "NOT_EXECUTED")

    def test_17_static_is_never_a_live_functional_pass(self):
        runner = self._new_runner(mode="static")
        runner.transport = MockTransport([])
        runner.client = pr.JmapClient(runner.transport, runner.args.jmap_url)
        runner.execute()
        report = runner.report()
        self.assertEqual(report["summary"]["overall"], "NOT_EXECUTED")
        self.assertFalse(report["live_functional_test"])
        self.assertEqual(pr.EXIT_CODES["NOT_EXECUTED"], 0)

    # -- ownership lifecycle ----------------------------------------------
    def test_18_create_success_readback_failure_uses_id_only_reconciliation(self):
        def script(r):
            return [
                session_response(),
                jmap(("x:Domain/query", {"ids": ["d1"]}, "dq")),
                jmap(("x:Domain/get", {"data": [{"id": "d1", "name": DOMAIN}]}, "dg")),
                jmap(("x:Account/set", {"created": {"new1": {"id": "a1"}}}, "ac")),
                jmap(("x:Account/get", {"data": []}, "ag")),
                jmap(("x:Account/get", {"data": []}, "rg")),
                jmap(("x:Account/get", {"data": [{"id": "a1", "name": r.localpart}]}, "vg")),
                jmap(("x:Account/set", {"destroyed": ["a1"]}, "dd")),
            ]
        runner = self._run_case(script)
        results = self.results(runner)
        self.assertEqual(results["T-003"].result, "FAIL")
        self.assertIn("MANUAL RECONCILIATION REQUIRED", results["T-003"].failure_reason)
        self.assertEqual(results["T-005"].result, "PASS")
        bodies = [call["body"] for call in runner.transport.calls]
        self.assertTrue(any('"rg"' in b for b in bodies), "id-based reconciliation was not attempted")
        self.assertFalse(any("x:Account/query" in b for b in bodies),
                         "runner searched accounts by name")

    def test_19_ambiguous_creation_reports_manual_reconciliation_without_guessing(self):
        def script(r):
            return base_script(r)[:3] + [jmap(("x:Account/set", {
                "created": {"new1": {"id": "a1"}, "new2": {"id": "a2"}}}, "ac"))]
        runner = self._run_case(script)
        results = self.results(runner)
        self.assertEqual(results["T-003"].result, "FAIL")
        self.assertIn("MANUAL RECONCILIATION REQUIRED", results["T-003"].failure_reason)
        bodies = [call["body"] for call in runner.transport.calls]
        self.assertFalse(any("destroy" in b for b in bodies), "ambiguous result triggered a destroy")

    # -- JMAP response validation -----------------------------------------
    def test_20_duplicate_call_id_rejected(self):
        def script(r):
            return [session_response(), jmap(
                ("x:Domain/query", {"ids": ["d1"]}, "dq"),
                ("x:Domain/query", {"ids": []}, "dq"))]
        results = self.results(self._run_case(script))
        self.assertEqual(results["T-002"].result, "FAIL")
        self.assertIn("duplicate call id", results["T-002"].failure_reason)

    def test_21_missing_call_id_rejected(self):
        def script(r):
            return [session_response(), jmap()]
        results = self.results(self._run_case(script))
        self.assertEqual(results["T-002"].result, "FAIL")
        self.assertIn("missing method responses", results["T-002"].failure_reason)

    def test_22_incorrect_method_name_rejected(self):
        def script(r):
            return [session_response(), jmap(("x:Domain/get", {"data": []}, "dq"))]
        results = self.results(self._run_case(script))
        self.assertEqual(results["T-002"].result, "FAIL")
        self.assertIn("method name mismatch", results["T-002"].failure_reason)

    # -- eventual consistency ---------------------------------------------
    def test_23_delayed_email_visibility_polls_to_success(self):
        def script(r):
            s = base_script(r)
            return s[:5] + [
                jmap(("Email/query", {"ids": []}, "eq")),
                jmap(("Email/query", {"ids": ["e1"]}, "eq")),
                jmap(("Email/get", {"data": [
                    {"id": "e1", "subject": r.subject_token + " local",
                     "to": [{"email": f"{r.alias_name}@{DOMAIN}"}]}]}, "eg")),
                s[7], s[8],
            ]
        results = self.results(self._run_case(
            script, extra=["--poll-deadline", "1", "--poll-interval", "0"]))
        self.assertEqual(results["T-004"].result, "PASS")
        self.assertIn("poll_attempts=2", results["T-004"].actual)

    def test_24_polling_timeout_fails_with_evidence(self):
        empty = jmap(("Email/query", {"ids": []}, "eq"))
        def fallback(body):
            if "Email/query" in body:
                return empty
            if "x:Account/get" in body:
                return jmap(("x:Account/get", {"data": []}, "vg"))
            if "x:Account/set" in body:
                return jmap(("x:Account/set", {"destroyed": []}, "dd"))
            raise AssertionError("unexpected mocked request")
        def script(r):
            return base_script(r)[:5] + [empty]
        results = self.results(self._run_case(
            script, default_response=fallback,
            extra=["--poll-deadline", "0.05", "--poll-interval", "0.01"]))
        self.assertEqual(results["T-004"].result, "FAIL")
        self.assertIn("not visible via JMAP", results["T-004"].failure_reason)
        self.assertIn("timed_out=True", results["T-004"].failure_reason)

    # -- external vantage and TLS -----------------------------------------
    def test_25_missing_external_vantage_marks_all_external_tests_blocked(self):
        runner = self._run_case(
            lambda r: [], mode="external",
            extra=["--external-smtp-host", "8.8.8.8",
                   "--external-authorized", "--confirm-external", "8.8.8.8"])
        results = self.results(runner)
        self.assertEqual(results["T-E00"].result, "BLOCKED")
        for test_id in ("T-E01", "T-E02", "T-E03"):
            self.assertEqual(results[test_id].result, "BLOCKED", test_id)
        self.assertEqual(runner.report()["summary"]["overall"], "BLOCKED")

    def test_26_starttls_absent_or_failing_never_passes(self):
        absent = self.results(self._run_case(extra=["--starttls"], probe=no_starttls_probe))
        for test_id in ("T-T01", "T-T02", "T-T03"):
            self.assertEqual(absent[test_id].result, "FAIL", test_id)
        failing = self.results(self._run_case(extra=["--starttls"], probe=failing_tls_probe))
        for test_id in ("T-T01", "T-T02", "T-T03"):
            self.assertNotEqual(failing[test_id].result, "PASS", test_id)
        not_requested = self.results(self._run_case())
        self.assertEqual(not_requested["T-T02"].result, "BLOCKED")

    # -- credential protection --------------------------------------------
    def test_27_credential_leakage_in_exception_and_report_paths(self):
        token = "super-secret-token-xyz"
        runner = self._run_case(
            lambda r: [pr.Response(200, "not-json " + token)],
            extra=["--admin-token", token,
                   "--jmap-url", f"http://user:{token}@127.0.0.1:8080/jmap/?api_key={token}"],
            skip_secret_check=True)
        report_path = os.path.join(runner.evidence_dir, "report.json")
        paths = [report_path] + [os.path.join(runner.evidence_dir, name)
                                 for name in os.listdir(runner.evidence_dir)]
        for path in paths:
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
            self.assertNotIn(token, content, path)
            self.assertNotIn(runner._test_password, content, path)
            self.assertNotIn("user:", content, path)
        self.assertEqual(self.results(runner)["T-001"].result, "FAIL")


if __name__ == "__main__":
    unittest.main(verbosity=2)
