import mockResponse from "./mock/analyzeResponse.json";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";
const API_URL = import.meta.env.VITE_API_URL;

export async function analyzeText(text, contentType, intent) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 600));
    return mockResponse;
  }
  const res = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      content_type: contentType,
      ...(intent?.trim() && { intent: intent.trim() }),
    }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.error?.message || "Something went wrong");
  return data;
}