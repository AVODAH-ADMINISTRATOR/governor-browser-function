// Governor Browser Function — client for the AI Studio Build custom Gemini app.
// House rule: the client carries NO secrets and makes NO provider calls with
// credentials. It calls the house backend road, which reaches the Governor
// Browser Research Lab (127.0.0.1:8915) on the backend. Read-only research
// is ALLOW; the lab returns ESCALATE/DENY rulings untouched for Adam's word.

export interface GovernorResearchRequest {
  query: string;
  purpose: string;
  url?: string;
  mustContain?: string;
}

export interface GovernorResearchResponse {
  governor: "ALLOW" | "ESCALATE" | "DENY";
  finding?: string;
  sourceUrl?: string;
  checkedAt?: string;
  state?: string;
  reason?: string;
}

const BACKEND_ROAD = "/v1/browser"; // house backend prefix for the lab

export async function governorBrowserResearch(
  req: GovernorResearchRequest,
): Promise<GovernorResearchResponse> {
  const res = await fetch(`${BACKEND_ROAD}/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: req.query,
      purpose: req.purpose,
      url: req.url,
      must_contain: req.mustContain,
    }),
  });
  const data = await res.json();
  return {
    governor: data.governor,
    finding: data.finding,
    sourceUrl: data.source_url,
    checkedAt: data.checked_at,
    state: data.state,
    reason: data.reason,
  };
}

export async function governorBrowserJudge(
  action: string,
): Promise<{ governor: string; reason: string }> {
  const res = await fetch(`${BACKEND_ROAD}/judge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
  const data = await res.json();
  return { governor: data.governor, reason: data.reason };
}
