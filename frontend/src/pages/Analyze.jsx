import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeText } from "../api";

export default function Analyze() {
  const [text, setText] = useState("");
  const [contentType, setContentType] = useState("email");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const [intent, setIntent] = useState("");

  async function handleSubmit() {
    if (!text.trim()) {
      setError("Please paste some text first.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const result = await analyzeText(text, contentType, intent);
      navigate("/report", { state: { result } });
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl p-6 flex flex-col gap-4">
      <h1 className="text-2xl font-bold">Analyze your text</h1>

      <select
        value={contentType}
        onChange={(e) => setContentType(e.target.value)}
        className="rounded border p-2"
      >
        <option value="instagram_post">Instagram post</option>
<option value="email">Email</option>
<option value="blog">Blog</option>
<option value="ad">Ad</option>
<option value="other">Other</option>
      </select>

      <input
  value={intent}
  onChange={(e) => setIntent(e.target.value)}
  placeholder="Intent (optional): what should this text achieve?"
  className="rounded border p-3"
/>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={10}
        placeholder="Paste your text here..."
        className="rounded border p-3"
      />

      {error && <p className="text-red-600">{error}</p>}

      <button
        onClick={handleSubmit}
        disabled={loading}
        className="rounded-lg bg-black px-6 py-3 text-white disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </main>
  );
}