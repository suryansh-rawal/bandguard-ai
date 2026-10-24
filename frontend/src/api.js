// The frontend only sends text and shows what the backend returns.
// All checking happens in the backend (see API_CONTRACT.md).
import mockResponse from "./mock/analyzeResponse.json";

export const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

// Temporary: auto-login with the demo user until the real login screen (S9) exists.
const DEMO_EMAIL = import.meta.env.VITE_DEMO_EMAIL || "creator@abc.com";
const DEMO_PASSWORD = import.meta.env.VITE_DEMO_PASSWORD || "demo123";

const getToken = () => {
  try { return localStorage.getItem("bg_token"); } catch { return null; }
};
const setToken = (t) => {
  try { localStorage.setItem("bg_token", t); } catch { /* ignore */ }
};

const networkError = () => new Error("Could not reach the server. Check that the backend is running.");

async function readJson(res) {
  try { return await res.json(); } catch { return null; }
}

function errorFrom(res, data, fallback) {
  const d = data?.error?.message || (typeof data?.detail === "string" ? data.detail : null);
  const err = new Error(d || fallback);
  err.status = res.status;
  return err;
}

export async function login(email = DEMO_EMAIL, password = DEMO_PASSWORD) {
  let res;
  try {
    res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
  } catch {
    throw networkError();
  }
  const data = await readJson(res);
  if (!res.ok) throw errorFrom(res, data, "Login failed.");
  const token = data?.token ?? data?.access_token;
  if (!token) throw new Error("Login worked but no token came back.");
  setToken(token);
  return data;
}

async function send(path, init) {
  const headers = { ...(init.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  try {
    return await fetch(`${API_URL}${path}`, { ...init, headers });
  } catch {
    throw networkError();
  }
}

// Sends the request; if the server says "not logged in", logs in once and retries.
async function request(path, init, fallback = "Something went wrong. Please try again.") {
  let res = await send(path, init);
  if (res.status === 401 || res.status === 403) {
    await login();
    res = await send(path, init);
  }
  const data = await readJson(res);
  if (!res.ok) throw errorFrom(res, data, fallback);
  return data;
}

const json = (body) => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

// Turns the backend response into the shape the UI uses.
// Accepts both the contract format and the format the backend sends today.
const SEVERITY = { critical: "high", warning: "medium", suggestion: "low" };

function normalize(data, text) {
  const issues = (data?.issues || []).map((x, i) => {
    const sourceIsText = typeof x.source === "string";
    const sourceId = x.source_id ?? x.source?.id ?? "";
    return {
      id: x.id ?? `i${i + 1}`,
      type: x.type ?? "other",
      severity: SEVERITY[x.severity] ?? x.severity ?? "low",
      original_text: x.original_text ?? x.matched_text ?? "",
      start: x.start ?? x.start_offset,
      end: x.end ?? x.end_offset,
      reason: x.reason ?? "",
      source:
        x.source == null
          ? null
          : sourceIsText
            ? { kind: /^(F-|FACT)/i.test(sourceId) ? "fact" : "guideline", id: sourceId, excerpt: x.source }
            : x.source,
      suggested_fix: x.suggested_fix ?? null,
      confidence: x.confidence ?? 0,
      needs_human: x.needs_human ?? x.severity === "critical",
      status: x.status ?? "open",
    };
  });
  const count = (s) => issues.filter((i) => i.severity === s).length;
  const status = ["green", "yellow", "red"].includes(data?.status)
    ? data.status
    : data?.confidence_rating ?? (issues.length ? "yellow" : "green");
  return {
    report_id: data?.report_id ?? data?.document_id ?? null,
    status,
    masked_text: data?.masked_text ?? text,
    pii_masked: data?.pii_masked ?? false,
    ai_used: data?.ai_used,
    issues,
    summary: { total: issues.length, high: count("high"), medium: count("medium"), low: count("low") },
  };
}

// POST /analyze
export async function analyzeText(text, contentType, intent = "") {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 600));
    return normalize(mockResponse, mockResponse.masked_text);
  }
  const data = await request("/analyze", json({ text, content_type: contentType, intent }));
  return normalize(data, text);
}

// POST /reports/{report_id}/issues/{issue_id}/action (contract section 4)
// If the backend does not have this route yet, the UI still works locally.
export async function sendAction(reportId, issueId, action, extra = {}) {
  if (USE_MOCK || !reportId) return null;
  try {
    return await request(
      `/reports/${reportId}/issues/${issueId}/action`,
      json({ action, edited_text: extra.edited_text ?? null, note: extra.note ?? null })
    );
  } catch (e) {
    if (e.status === 404 || e.status === 405) {
      console.warn("Action route not found on the backend yet.");
      return null;
    }
    throw e;
  }
}

// POST /upload (multipart) -> { text, filename }
export async function uploadFile(file, contentType) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 500));
    return { text: mockResponse.masked_text, filename: file.name };
  }
  const form = new FormData();
  form.append("file", file);
  form.append("content_type", contentType);
  return request("/upload", { method: "POST", body: form }, "The file could not be read.");
}