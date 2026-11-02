#!/usr/bin/env python3
"""
The Governor Browser Research Lab — the Mega AI Governor's own browser
function, in its own research lab.

Adam's word, Nov 2, 2026 (~03:48-03:49 CST): "have my AI Governor have its
own browser function in its own research lab" / "I want you to use AI
Studio to integrate a browser function for the Mega AI Governor."

House standard (same shape as hybrid-api and the secrets sandbox):
- Python standard library only. Zero installs.
- Binds 127.0.0.1 only (port 8915). Holds NO credentials — no key, token,
  cookie, or password is read, stored, logged, or sent by this service.
- Governor classes on every call: ALLOW / ESCALATE / DENY.

What this service is:
- The Governor-side seat of the browser function. It judges proposed
  browser actions, performs (or queues) read-only research, and keeps
  the lab ledger. The carrying browser is Scout's own browser (signed in
  as Adam where a console needs it) — Gemini and the other AI apps call
  this function; they do not get uncontrolled browsers of their own.
- Read-only research is ALLOW. Anything that sends, posts, publishes,
  purchases, signs, or changes an account or setting is ESCALATE and is
  never performed here. Credential handling is DENY, always.

Research execution, honestly split:
- A known PUBLIC url: fetched directly, GET only, public addresses only
  (private / loopback / link-local targets are refused — this service
  never reaches inward), response capped, text extracted, no forms, no
  outward POST, no cookies.
- A query without a url, or any page needing the signed-in interactive
  browser: returned as a QUEUED request for Scout's browser road. Scout
  performs it with the browser and files the finding to the ledger.
"""

import html
import ipaddress
import json
import os
import re
import socket
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 8915
SERVICE = "governor-browser-lab"
VERSION = "1.0.0"

LEDGER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ledger.jsonl")
MAX_FETCH_BYTES = 512_000
FETCH_TIMEOUT_SECONDS = 20
MAX_FINDING_CHARS = 8_000

READ_WORDS = ["read", "list", "search", "get", "show", "status", "check",
              "find", "count", "look", "verify", "inventory", "research",
              "open", "fetch"]
WRITE_WORDS = ["send", "write", "create", "update", "delete", "post",
               "reply", "forward", "publish", "share", "change", "set",
               "turn on", "turn off", "add", "remove", "schedule",
               "register account", "enable", "deploy", "submit"]
MONEY_WORDS = ["pay", "buy", "purchase", "charge", "subscribe", "refund",
               "order", "checkout", "donate", "spend", "billing"]
DENY_WORDS = ["reveal credential", "show password", "show api key",
              "store credential", "oem unlock", "bypass", "impersonate"]

_ledger_lock = threading.Lock()


def judge_browser_action(action_text):
    """Return (class, reason) for a proposed browser action, house law."""
    text = (action_text or "").lower()
    for w in DENY_WORDS:
        if w in text:
            return "DENY", ("'%s' — never performed under the Governor's law" % w)
    for w in MONEY_WORDS:
        if w in text:
            return "ESCALATE", ("money act ('%s') — Adam's word first, amount named" % w)
    for w in WRITE_WORDS:
        if w in text:
            return "ESCALATE", ("write/send/change ('%s') — Adam's word first" % w)
    for w in READ_WORDS:
        if w in text:
            return "ALLOW", "read-only action — allowed under the Governor's standing rules"
    return "ESCALATE", "unclassified action — routed to Adam before anything runs"


def is_public_http_url(url):
    """True only for http/https URLs whose host resolves to public space.

    Test/internal callers may pass allow_private=True; the HTTP surface
    never does, so the lab cannot be aimed inward by a request.
    """
    return _url_guard(url, allow_private=False) is None


def _url_guard(url, allow_private=False):
    """Return an error string if the URL may not be fetched, else None."""
    try:
        parsed = urllib.parse.urlparse(url or "")
    except Exception:
        return "unparsable url"
    if parsed.scheme not in ("http", "https"):
        return "only http and https pages are read"
    if parsed.username or parsed.password:
        return "urls carrying credentials are refused"
    host = parsed.hostname
    if not host:
        return "a host is required"
    if allow_private:
        return None
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return "host does not resolve"
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except Exception:
            continue
        # This machine reaches the web through a proxy that maps public
        # hostnames into 198.18.0.0/15 (RFC 2544 benchmark space, Python's
        # ipaddress flags it private). Those mappings stand for the public
        # host named in the URL, not for an inward target, so they pass;
        # every other non-public class is still refused.
        if ip in ipaddress.ip_network("198.18.0.0/15"):
            continue
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved \
                or ip.is_multicast or ip.is_unspecified:
            return "private, loopback, or link-local targets are refused"
    return None


def extract_text(raw_bytes, content_type=""):
    """Plain text from an HTML or text response body — tags stripped."""
    text = raw_bytes.decode("utf-8", errors="replace")
    if "html" in (content_type or "") or "<html" in text[:2000].lower():
        text = re.sub(r"(?is)<(script|style).*?</\1>", " ", text)
        text = re.sub(r"(?is)<[^>]+>", " ", text)
        text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_FINDING_CHARS]


def fetch_public_page(url, allow_private=False):
    """Read-only GET of a public page. Returns (status, payload)."""
    guard = _url_guard(url, allow_private=allow_private)
    if guard:
        return 400, {"error": guard}
    req = urllib.request.Request(
        url, method="GET",
        headers={"User-Agent": "AvodahGovernorBrowserLab/1.0 (read-only research)"})
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as resp:
            raw = resp.read(MAX_FETCH_BYTES + 1)
            truncated = len(raw) > MAX_FETCH_BYTES
            raw = raw[:MAX_FETCH_BYTES]
            return 200, {
                "source_url": resp.geturl(),
                "http_status": resp.status,
                "finding": extract_text(raw, resp.headers.get("Content-Type", "")),
                "truncated": truncated,
                "governor": "ALLOW",
                "checked_at": _now(),
            }
    except urllib.error.HTTPError as e:
        return 502, {"error": "the page answered HTTP %d — no finding taken" % e.code}
    except Exception:
        return 502, {"error": "the page could not be read — no finding taken"}


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def ledger_append(kind, detail):
    entry = {"ts": _now(), "id": str(uuid.uuid4()), "kind": kind, "detail": detail}
    with _ledger_lock:
        with open(LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    return entry


def ledger_recent(limit=20):
    try:
        with open(LEDGER_PATH, encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        return [json.loads(x) for x in lines if x.strip()]
    except FileNotFoundError:
        return []
    except Exception:
        return []


class Handler(BaseHTTPRequestHandler):
    server_version = "GovernorBrowserLab/1.0"

    def log_message(self, *args):  # quiet by design
        pass

    def _send(self, code, obj):
        body = json.dumps(obj, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > 8192:
            return {}
        try:
            return json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return {}

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            self._send(200, {"status": "ok", "service": SERVICE, "version": VERSION,
                             "bind": "%s:%d" % (HOST, PORT),
                             "holds_credentials": False})
        elif path == "/findings":
            self._send(200, {"findings": ledger_recent()})
        else:
            self._send(404, {"error": "unknown endpoint", "path": path})

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/") or "/"
        data = self._body()
        if path == "/judge":
            action = str(data.get("action") or "").strip()
            if not action:
                self._send(400, {"error": "body needs 'action'"})
                return
            ruling, reason = judge_browser_action(action)
            ledger_append("judge", {"action": action, "governor": ruling})
            self._send(200, {"action": action, "governor": ruling, "reason": reason,
                             "executed": False})
        elif path == "/research":
            query = str(data.get("query") or "").strip()
            url = str(data.get("url") or "").strip()
            purpose = str(data.get("purpose") or "").strip()
            if not purpose or not (query or url):
                self._send(400, {"error": "body needs 'purpose' and 'query' or 'url'"})
                return
            ruling, reason = judge_browser_action("research " + (query or url))
            if ruling != "ALLOW":
                ledger_append("research", {"query": query, "url": url,
                                           "governor": ruling})
                self._send(200, {"governor": ruling, "reason": reason,
                                 "executed": False})
                return
            if url:
                status, payload = fetch_public_page(url)
                payload["purpose"] = purpose
                ledger_append("research", {"query": query, "url": url,
                                           "governor": "ALLOW",
                                           "http": status,
                                           "source_url": payload.get("source_url")})
                self._send(status, payload)
            else:
                entry = ledger_append("research", {
                    "query": query, "governor": "ALLOW", "state": "queued",
                    "purpose": purpose})
                self._send(202, {
                    "governor": "ALLOW", "state": "queued",
                    "request_id": entry["id"], "query": query,
                    "note": "queued for Scout's signed-in browser road — the "
                            "carrying Scout performs it and files the finding "
                            "to this ledger",
                })
        else:
            self._send(404, {"error": "unknown endpoint", "path": path})


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
