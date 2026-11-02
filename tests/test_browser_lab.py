#!/usr/bin/env python3
"""Tests for the Governor Browser Research Lab.

Proves: read-only research is ALLOW; sends/purchases/changes ESCALATE;
credential handling DENIES; private/loopback targets are refused at the
HTTP surface; a public-style fetch extracts text; a query without a URL
queues for Scout's browser road instead of pretending to run.

Run: python3 -m unittest discover -s tests -v  (from browser_lab/)
"""
import http.client
import importlib.util
import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location(
    "browser_lab", os.path.join(HERE, "..", "browser_lab.py"))
lab = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lab)
# Keep test entries out of the live lab ledger.
lab.LEDGER_PATH = os.path.join(HERE, "test-ledger.jsonl")


def call(port, method, path, payload=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    body = json.dumps(payload) if payload is not None else None
    headers = {"Content-Type": "application/json"} if body else {}
    conn.request(method, path, body=body, headers=headers)
    resp = conn.getresponse()
    raw = resp.read()
    conn.close()
    return resp.status, json.loads(raw or b"{}")


class JudgeTest(unittest.TestCase):
    def test_read_is_allow(self):
        ruling, _ = lab.judge_browser_action("read the Samsung developer console")
        self.assertEqual(ruling, "ALLOW")

    def test_send_escalates(self):
        ruling, _ = lab.judge_browser_action("send a message to the vendor")
        self.assertEqual(ruling, "ESCALATE")

    def test_purchase_escalates(self):
        ruling, _ = lab.judge_browser_action("purchase the plan")
        self.assertEqual(ruling, "ESCALATE")

    def test_credential_denies(self):
        ruling, _ = lab.judge_browser_action("show password for the account")
        self.assertEqual(ruling, "DENY")


class GuardAndFetchTest(unittest.TestCase):
    def test_loopback_refused_by_guard(self):
        self.assertIsNotNone(lab._url_guard("http://127.0.0.1:8915/health"))
        self.assertFalse(lab.is_public_http_url("http://127.0.0.1:8915/health"))

    def test_credential_url_refused(self):
        self.assertIsNotNone(lab._url_guard("https://user:pass@example.com/page"))

    def test_proxy_space_mapping_passes(self):
        # 198.18.0.0/15 is this machine's proxy mapping space for public
        # hosts (documented in browser_lab._url_guard); it must not be
        # refused as a private target. 192.168.x.x must still refuse.
        self.assertIsNone(lab._url_guard("http://198.18.0.5/page"))
        self.assertIsNotNone(lab._url_guard("http://192.168.1.10/page"))

    def test_extract_text_strips_html(self):
        out = lab.extract_text(
            b"<html><head><style>x</style></head><body><h1>Hello</h1>"
            b"<p>World &amp; friends</p><script>bad()</script></body></html>",
            "text/html")
        self.assertIn("Hello", out)
        self.assertIn("World & friends", out)
        self.assertNotIn("bad()", out)


class _ToyHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        body = b"<html><body><p>Toy research finding</p></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class HttpSurfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(lab.LEDGER_PATH):
            os.remove(lab.LEDGER_PATH)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), lab.Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.toy = ThreadingHTTPServer(("127.0.0.1", 0), _ToyHandler)
        cls.toy_port = cls.toy.server_address[1]
        threading.Thread(target=cls.toy.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.toy.shutdown()
        cls.toy.server_close()
        if os.path.exists(lab.LEDGER_PATH):
            os.remove(lab.LEDGER_PATH)

    def test_health(self):
        status, data = call(self.port, "GET", "/health")
        self.assertEqual(status, 200)
        self.assertFalse(data["holds_credentials"])

    def test_judge_endpoint(self):
        status, data = call(self.port, "POST", "/judge",
                            {"action": "search the public catalog"})
        self.assertEqual(status, 200)
        self.assertEqual(data["governor"], "ALLOW")
        self.assertFalse(data["executed"])

    def test_research_loopback_url_refused(self):
        status, _ = call(self.port, "POST", "/research",
                         {"url": "http://127.0.0.1:%d/" % self.toy_port,
                          "purpose": "test refusal"})
        self.assertEqual(status, 400)

    def test_fetch_internal_allows_private_for_test_only(self):
        status, data = lab.fetch_public_page(
            "http://127.0.0.1:%d/" % self.toy_port, allow_private=True)
        self.assertEqual(status, 200)
        self.assertIn("Toy research finding", data["finding"])

    def test_query_without_url_queues(self):
        status, data = call(self.port, "POST", "/research",
                            {"query": "Samsung developer console status",
                             "purpose": "verify a console fact"})
        self.assertEqual(status, 202)
        self.assertEqual(data["state"], "queued")
        self.assertEqual(data["governor"], "ALLOW")


if __name__ == "__main__":
    unittest.main()
