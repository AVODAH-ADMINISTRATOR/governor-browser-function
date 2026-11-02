#!/usr/bin/env python3
"""Governor Browser Function — server-side client for the lab service.

Used by the Firebase-road bridge worker and the GitHub/custom-API bridge.
Server-side only, per the house rule: no secrets or service calls live in
client code. Holds no credentials; it speaks plain JSON to the lab on the
loopback backend (127.0.0.1:8915).
"""
import json
import urllib.request

LAB = "http://127.0.0.1:8915"


def _post(path, payload):
    req = urllib.request.Request(
        LAB + path, method="POST",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, json.loads(resp.read() or b"{}")


def governor_browser_research(query="", url="", purpose="", must_contain=""):
    """Ask the Governor's lab for a read-only finding (ALLOW class)."""
    return _post("/research", {"query": query, "url": url,
                               "purpose": purpose,
                               "must_contain": must_contain})


def governor_browser_judge(action):
    """Ask the Governor to rule on a proposed browser action first."""
    return _post("/judge", {"action": action})
