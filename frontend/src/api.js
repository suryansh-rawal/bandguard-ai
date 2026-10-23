// The frontend only sends text and shows what the backend returns.
// All checking happens in the backend (see API_CONTRACT.md).
import mockResponse from "./mock/analyzeResponse.json";

export const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, body) {
  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new Error("Could not reach the server. Check that the backend is running.");
  }
  let data = null;
  try {
    data = await res.json();
  } catch {
    /* body was not JSON */
  }
  if (!res.ok) throw new Error(data?.error?.message || "Something went wrong. Please try again.");
  return data;
}

// POST /analyze
export async function analyzeText(text, contentType, intent = "") {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 600));
    return mockResponse; // contract example, section 1
  }
  return request("/analyze", { text, content_type: contentType, intent });
}

// POST /reports/{report_id}/issues/{issue_id}/action
export async function sendAction(reportId, issueId, action, extra = {}) {
  if (USE_MOCK) return null;
  return request(`/reports/${reportId}/issues/${issueId}/action`, {
    action, // accept | edit | dispute
    edited_text: extra.edited_text ?? null,
    note: extra.note ?? null,
  });
}

// POST /upload (multipart) -> { text, filename }. The text is then sent to /analyze.
export async function uploadFile(file, contentType) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 500));
    return { text: mockResponse.masked_text, filename: file.name };
  }
  const form = new FormData();
  form.append("file", file);
  form.append("content_type", contentType);
  let res;
  try {
    res = await fetch(`${API_URL}/upload`, { method: "POST", body: form });
  } catch {
    throw new Error("Could not reach the server. Check that the backend is running.");
  }
  let data = null;
  try {
    data = await res.json();
  } catch {
    /* body was not JSON */
  }
  if (!res.ok) throw new Error(data?.error?.message || "The file could not be read.");
  return data;
}