import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeText, uploadFile } from "../api";
import { TYPES, SAMPLES, INTENT_GROUPS, FONTS, WEIGHTS, COLORS } from "../options";

const field =
  "w-full rounded-xl border border-latte/70 bg-white/70 px-4 py-3 text-ink placeholder:text-latte focus:border-burgundy";

function Card({ n, title, hint, children }) {
  return (
    <section className="glass rounded-2xl p-5 sm:p-6">
      <div className="flex items-center gap-3">
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-burgundy text-sm font-medium text-ivory">
          {n}
        </span>
        <h2 className="font-display text-2xl font-semibold leading-tight text-burgundy">{title}</h2>
        {hint && <p className="hidden text-sm text-ink/60 sm:block">{hint}</p>}
      </div>
      <div className="mt-4">{children}</div>
    </section>
  );
}

export default function Analyze() {
  const nav = useNavigate();
  const fileRef = useRef(null);
  const [contentType, setContentType] = useState("instagram_post");
  const [text, setText] = useState("");
  const [fileName, setFileName] = useState("");
  const [intent, setIntent] = useState("");
  const [group, setGroup] = useState(INTENT_GROUPS[0].id);
  const [design, setDesign] = useState({
    fontFamily: FONTS[0].css,
    fontSize: 18,
    lineHeight: 1.6,
    fontWeight: "400",
    color: "#111827",
  });
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const setD = (k, v) => setDesign((d) => ({ ...d, [k]: v }));
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  const items = INTENT_GROUPS.find((g) => g.id === group).items;

  async function onFile(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setError("");
    setUploading(true);
    try {
      const data = await uploadFile(file, contentType);
      setText(data.text);
      setFileName(data.filename || file.name);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function submit() {
    if (!text.trim()) {
      setError("Please enter some text to check.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const report = await analyzeText(text, contentType, intent.trim());
      nav("/report", { state: { report, text, intent: intent.trim(), contentType, design } });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-5xl space-y-5 px-6 py-10">
      <header>
        <h1 className="font-display text-5xl font-semibold gradient-text">Check your content</h1>
        <p className="mt-2 text-ink/70">
          Tell us what you are writing and what it should achieve. We check it against your brand rules.
        </p>
      </header>

      {/* 1. Content */}
      <Card n="1" title="Your content" hint="Write it, paste it, or upload a Word or PDF file.">
        <div className="flex flex-wrap gap-2">
          {TYPES.map((t) => (
            <button key={t.id} onClick={() => setContentType(t.id)} className={`chip px-4! py-2! text-sm! ${contentType === t.id ? "chip-active" : ""}`}>
              {t.label}
            </button>
          ))}
        </div>
        <textarea
          className={`${field} mt-4 resize-y`}
          rows={7}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Write or paste your text here"
        />
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <input ref={fileRef} type="file" accept=".docx,.pdf" className="hidden" onChange={onFile} />
          <button onClick={() => fileRef.current?.click()} disabled={uploading} className="chip px-4! py-2! text-sm!">
            {uploading ? "Reading file..." : "Upload .docx or .pdf"}
          </button>
          {fileName && <span className="text-sm text-ink/60">{fileName}</span>}
          <span className="mx-1 hidden h-5 w-px bg-latte/60 sm:block" />
          <span className="text-sm text-ink/60">Try a sample:</span>
          {SAMPLES.map((s) => (
            <button key={s.label} className="chip" onClick={() => { setText(s.text); setContentType(s.type); setFileName(""); }}>
              {s.label}
            </button>
          ))}
          <span className="ml-auto text-sm text-ink/50">{words} word{words === 1 ? "" : "s"}</span>
        </div>
      </Card>

      {/* 2. Goal */}
      <Card n="2" title="What should this text achieve?" hint="Pick an idea or write your own. Optional.">
        <input className={field} value={intent} onChange={(e) => setIntent(e.target.value)} placeholder="e.g. Promote the app and create urgency" />
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {INTENT_GROUPS.map((g) => (
            <button key={g.id} onClick={() => setGroup(g.id)} className={`chip ${group === g.id ? "chip-active" : ""}`}>
              {g.label}
            </button>
          ))}
          <span className="mx-1 hidden h-5 w-px bg-latte/60 sm:block" />
          {items.map((it) => (
            <button key={it} onClick={() => setIntent(it)} className={`chip ${intent === it ? "chip-active" : ""}`}>
              {it}
            </button>
          ))}
        </div>
      </Card>

      {/* 3. Design */}
      <Card n="3" title="Design your text" hint="Choose how the final text should look.">
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-5">
            <div className="rounded-xl border border-latte/50 bg-white p-4">
              <p
                className="min-h-16 wrap-break-word"
                style={{ fontFamily: design.fontFamily, fontSize: design.fontSize, lineHeight: design.lineHeight, fontWeight: design.fontWeight, color: design.color }}
              >
                {text.trim() ? text.slice(0, 100) + (text.length > 100 ? "..." : "") : "Your text will look like this."}
              </p>
            </div>

            <div>
              <p className="mb-2 text-sm font-medium">Weight</p>
              <div className="flex gap-2">
                {WEIGHTS.map((w) => (
                  <button key={w.v} onClick={() => setD("fontWeight", w.v)} className={`chip px-4! py-2! text-sm! ${design.fontWeight === w.v ? "chip-active" : ""}`} style={{ fontWeight: w.v }}>
                    {w.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <label className="text-sm font-medium">
                Size: {design.fontSize}px
                <input type="range" min="12" max="40" className="mt-2 w-full accent-burgundy" value={design.fontSize} onChange={(e) => setD("fontSize", +e.target.value)} />
              </label>
              <label className="text-sm font-medium">
                Line spacing: {design.lineHeight}
                <input type="range" min="1" max="2.4" step="0.1" className="mt-2 w-full accent-burgundy" value={design.lineHeight} onChange={(e) => setD("lineHeight", +e.target.value)} />
              </label>
            </div>

            <div>
              <p className="mb-2 text-sm font-medium">Text colour</p>
              <div className="flex flex-wrap items-center gap-2">
                {COLORS.map((c) => (
                  <button
                    key={c.hex}
                    title={`${c.name}${c.brand ? " (brand colour)" : ""}`}
                    aria-label={c.name}
                    onClick={() => setD("color", c.hex)}
                    className={`h-8 w-8 rounded-full border-2 ${design.color.toLowerCase() === c.hex.toLowerCase() ? "border-burgundy" : "border-latte/60"} ${c.brand ? "ring-2 ring-latte/60 ring-offset-2 ring-offset-ivory" : ""}`}
                    style={{ background: c.hex }}
                  />
                ))}
                <input type="color" aria-label="Custom colour" className="h-8 w-10 cursor-pointer rounded-lg border border-latte/60 bg-white/70" value={design.color} onChange={(e) => setD("color", e.target.value)} />
              </div>
              <p className="mt-2 text-xs text-ink/50">Circles with a ring are your brand colours.</p>
            </div>
          </div>

          <div>
            <p className="mb-2 text-sm font-medium">Font</p>
            <div className="grid grid-cols-2 gap-2">
              {FONTS.map((f) => {
                const on = design.fontFamily === f.css;
                return (
                  <button
                    key={f.label}
                    onClick={() => setD("fontFamily", f.css)}
                    className={`rounded-xl border px-3 py-2 text-left transition ${on ? "border-burgundy bg-burgundy/5" : "border-latte/60 bg-white/50 hover:border-burgundy"}`}
                  >
                    <span className="block truncate text-lg leading-tight" style={{ fontFamily: f.css }}>{f.label}</span>
                    <span className="text-xs text-ink/60">{f.brand ? "Brand font" : f.kind}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </Card>

      <div className="mx-auto max-w-xl pt-2">
        {error && <p role="alert" className="mb-3 rounded-lg bg-red-50 p-3 text-sm text-red-800">{error}</p>}
        <button onClick={submit} disabled={loading} className="btn-neon w-full rounded-full px-8 py-4 text-lg">
          {loading ? "Checking your content..." : "Check content"}
        </button>
      </div>
    </main>
  );
}