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
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, headers=None, body=None):
        self.calls.append({"method": method, "url": url, "body": body or ""})
        if not self.responses:
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
            {"id": "e1", "subject": runner.subject_token + " local"}]}, "eg")),
        jmap(("x:Account/get", {"data": [{"id": "a1", "name": runner.localpart}]}, "vg")),
        jmap(("x:Account/set", {"destroyed": ["a1"]}, "dd")),
    ]


class RunnerMockTests(unittest.TestCase):
    def _new_runner(self, smtp=ok_smtp, mode="local", extra=None):
        tmp = tempfile.mkdtemp(prefix="domibox-poc-test-")
        argv = [
            "--mode", mode,
            "--report-dir", tmp,
            "--jmap-url", "http://127.0.0.1:8080/jmap/",
            "--domain", DOMAIN,
            "--admin-user", "poc-admin@example.invalid",
            "--admin-password", SECRET,
        ]
        if mode == "local":
            argv += ["--local-authorized", "--confirm-local", "LOCAL-POC"]
        elif mode == "external":
            argv += ["--external-authorized"]
        if extra:
            argv += extra
        args = pr.build_parser().parse_args(argv)
        runner = pr.Runner(args, transport=MockTransport([]), smtp_sender=smtp)
        return runner

    def _run_case(self, script_builder=base_script, smtp=ok_smtp, extra=None):
        runner = self._new_runner(smtp=smtp, extra=extra)
        runner.transport = MockTransport(script_builder(runner))
        runner.client = pr.JmapClient(
            runner.transport, runner.args.jmap_url,
            runner.args.admin_user, runner.args.admin_password,
        )
        runner.execute()
        report_path = runner.write_report()
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
        self.assertIn("message not found", results["T-004"].failure_reason)
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
        self.assertIn("no account id", results["T-003"].failure_reason)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
