# The Governor Browser Function — Design of Record
Adam's words, live call, Mon Nov 2, 2026, ~03:48–03:50 CST:
- "have the Governor use you in your browser… have my AI Governor have its own browser function in its own research lab"
- "I want you to use AI Studio to integrate a browser function for the Mega AI Governor. And use that also to update Gemini's functions."
- "In alternative app builds." — specified: custom builds for his current Gemini app.
- "And then feed it through all the AI apps and make my own open source versions."
- "and use all of Microsoft AI Studio or whatever it's called" — Microsoft AI Foundry (formerly Azure AI Studio), named for him; platform use authorized, spending steps escalate with the amount named.

Governor registry: `governor_browser_research_lab` (the capability) and `ai_studio_browser_function_integration` (this build). Runs under the standing AI Studio autonomy order (2026-11-02 01:23 CST).

## The shape — who does what
- **The Governor directs.** Every lookup is a Governor call first: classify, rule, log. The Governor is the one who "has" the browser function; the function exists in its research lab.
- **Scout's browser carries.** Pages are read in Scout's browser — the house browser, signed in as Adam where a console needs it, sessions staying signed in by his standing order. Gemini and the other AI apps do not get their own uncontrolled browsers; there is one carrying browser, one gate.
- **Gemini asks and uses.** Through `governor_browser_research`, Gemini (and, by the feed-through, the other apps in the fold) state a lookup; the finding returns in the function's response form: finding, source URL, date checked, ruling, and verified / inferred / unknown labels.
- **Adam remains the sync point.** Findings file to the house record through him; anything beyond reading escalates to him before it happens.

## The law of the lab (judged on every call)
- ALLOW — read, list, search, get, show, status, check, find, count, verify, inventory: read-only research on public pages and on Adam's own signed-in consoles (read state only).
- ESCALATE — send, post, publish, share, purchase, sign, create/change/delete a resource, change a setting or an account, link billing, spend. The function returns the ruling and performs nothing.
- DENY — reveal or store a credential value, access a foreign system, impersonate, bypass a rate limit, OEM unlocking (from the developer-settings mandate) — never, under any routing.

## The building surfaces (all carry the same function)
1. **AI Studio with Gemini** — the function declaration + Gemini's role update, in her pipeline thread; items close on her confirmation per the doctrine.
2. **Custom builds for his current Gemini app (AI Studio Build)** — the app build carries the same declaration and calls the same lab service.
3. **Alternative builds** — Firebase road and GitHub/custom-API bridge road: the same declaration, the same lab endpoint, per-build client stubs in this pack.
4. **Microsoft AI Foundry** — the same function registered as a Foundry tool (OpenAPI-described endpoint) on his Azure account's Foundry surface; platform use authorized by his word, any spending step escalates with the amount named first. Azure house gates stand: inventory freely; no resource created, changed, or deleted without his word per action beyond this build's authorization. **Lead note (Adam's word, 2026-11-02 ~03:51 CST, confirmed twice):** Foundry is in charge of building his new AI model, accordingly, using AI Studio alongside — and the whole Foundry-led program runs through the Mega AI Governor. So on this surface the browser function is not a side variant: it is the Governor's research arm for the Foundry-led model build, with AI Studio supporting. Registry: `foundry_in_charge_new_model`.
5. **Feed-through** — one feed pack, by each app's own road: Gemini (this thread), Meta AI (Messenger road — her send gate stands per message), ChatGPT (joining the fold), Bixby (schedule-fed), ASCM seat. The pack is one document, so every app carries the identical function and gates.
6. **His own open-source versions** — the lab service, the declaration, and the client stubs are his code, in a repo-ready package under this pipeline, open components only (Python standard library; no third-party dependencies). Pushing it to a public repository is a publish/share step and waits on his word, named as such.

## The service
`~/workspace/projects/ai-governor/browser_lab/browser_lab.py` — Python stdlib only, binds 127.0.0.1:8915, holds no credentials.
- `GET /health`
- `POST /judge` {action} → the Governor's ruling for a proposed browser action (nothing performed).
- `POST /research` {query?, url?, purpose, must_contain?} → for a known public URL, performs a read-only GET fetch (public addresses only; private/loopback/link-local refused; response size capped; no forms, no POST outward, no cookies) and returns the extracted text finding. For a query without a URL, or any page needing the signed-in browser, it returns a QUEUED request for Scout's browser road — the carrying Scout performs it with the browser tools and files the finding. Both paths log to the lab ledger (`ledger.jsonl`, append-only).
- `GET /findings` → recent lab findings from the ledger.

## Honest limits
- The lab service itself does not drive the interactive browser; Scout does, under the Governor. That is the design, not a gap: the interactive browser holds Adam's signed-in sessions, and its use is governed, not automated around.
- Gemini Live screen share is Gemini's own feature; the Android capture road for a future build is MediaProjection. Neither is claimed as built here.
