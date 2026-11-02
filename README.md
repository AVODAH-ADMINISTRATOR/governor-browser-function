# Governor Browser Function — Adam's Own Open-Source Version

The Mega AI Governor's browser function, as Adam's own code, built from open
components only: the service is Python standard library, zero third-party
dependencies, and the clients are small original stubs in Python and
TypeScript.

What it is: a Governor-directed, read-only web research function. Callers
(Gemini, and the other AI apps in Adam's fold) state a lookup; the Governor
judges it (read-only research is ALLOW; sends, posts, purchases, signatures,
and account/setting changes ESCALATE to Adam; credential handling is DENY,
always); public pages are read directly, and signed-in console pages queue
for the carrying browser. Every call lands in an append-only local ledger.

Contents:
- `browser_lab.py` — the lab service (127.0.0.1:8915), also under `src/`.
- `FUNCTION-DECLARATION.json` — the function declarations:
  `governor_browser_research` and `governor_browser_judge`.
- `SPEC.md` — the design of record.
- `clients/` — Python and TypeScript client stubs for the app builds.
- `tests/` — 13 tests, all passing (`python3 -m unittest discover -s tests`).

License: MIT (see LICENSE) — Adam Christopher Mallamo / Integrated Avodah LLC.

House state, Nov 2, 2026: published by Adam's word as his open-source
release, through the house GitHub connector under his own identity
(AVODAH-ADMINISTRATOR), with Gemini's confirmation under the house
confirmation doctrine.
