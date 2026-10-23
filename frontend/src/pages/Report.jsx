import { useEffect, useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import { sendAction, USE_MOCK } from "../api";

const STATUS_STYLE = {
  green: ["All clear", "bg-green-100 text-green-800"],
  yellow: ["Fixable issues", "bg-amber-100 text-amber-800"],
  red: ["Needs attention", "bg-red-100 text-red-800"],
};
const SEV_STYLE = {
  high: "bg-red-100 text-red-800",
  medium: "bg-amber-100 text-amber-800",
  low: "bg-stone-200 text-stone-700",
};
const TYPE_LABEL = {
  banned_term: "Banned term",
  preferred_term: "Preferred term",
  unsupported_claim: "Unsupported claim",
  fact_mismatch: "Fact mismatch",
  tone: "Tone",
  pii: "Private data",
  other: "Needs review",
};

export default function Report() {
  const { state } = useLocation();
  const [local, setLocal] = useState({}); // issue id -> accepted | edited | disputed
  const [edits, setEdits] = useState({}); // issue id -> edited text
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  // Always open at the top, where Before and After are
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  if (!state) return <Navigate to="/analyze" replace />;
  const { report, intent, design } = state;
  const base = report.masked_text ?? state.text;
  const issues = report.issues || [];

  const statusOf = (i) => local[i.id] || i.status || "open";
  const replacementOf = (i) => {
    const s = statusOf(i);
    if (s === "disputed") return null;
    if (s === "edited") return edits[i.id];
    return i.suggested_fix || null; // open / accepted
  };

  async function act(i, action, edited_text) {
    const next = { accept: "accepted", edit: "edited", dispute: "disputed" }[action];
    setError("");
    setLocal((s) => ({ ...s, [i.id]: next }));
    if (action === "edit") setEdits((e) => ({ ...e, [i.id]: edited_text }));
    try {
      await sendAction(report.report_id, i.id, action, { edited_text });
    } catch (e) {
      setError(e.message);
    }
  }

  // Place each issue in the text (use start/end, fall back to a text search)
  const placed = issues
    .map((i) => {
      let start = i.start;
      if (base.slice(i.start, i.end) !== i.original_text) start = base.indexOf(i.original_text);
      return start < 0 ? null : { i, start, end: start + i.original_text.length };
    })
    .filter(Boolean)
    .sort((a, b) => a.start - b.start);

  const before = [];
  const after = [];
  let pos = 0;
  placed.forEach(({ i, start, end }) => {
    if (start < pos) return;
    const plain = base.slice(pos, start);
    before.push({ t: plain }, { t: i.original_text, kind: "bad" });
    after.push({ t: plain });
    const rep = replacementOf(i);
    after.push(
      rep ? { t: rep, kind: i.source?.kind === "fact" ? "fact" : "fix", src: i.source?.id } : { t: i.original_text }
    );
    pos = end;
  });
  before.push({ t: base.slice(pos) });
  after.push({ t: base.slice(pos) });
  const finalText = after.map((s) => s.t).join("");

  const MARK = { bad: "bg-red-200", fix: "bg-green-200", fact: "bg-amber-200" };
  const show = (segs) =>
    segs.map((s, k) =>
      s.kind ? (
        <mark key={k} className={`${MARK[s.kind]} rounded px-0.5 text-inherit`}>
          {s.t}
          {s.src && <sup className="ml-0.5 text-[0.6em] opacity-70">{s.src}</sup>}
        </mark>
      ) : (
        <span key={k}>{s.t}</span>
      )
    );

  const textStyle = {
    fontFamily: design.fontFamily,
    fontSize: design.fontSize,
    lineHeight: design.lineHeight,
    fontWeight: design.fontWeight,
    color: design.color,
    whiteSpace: "pre-wrap",
  };

  async function copy() {
    try {
      await navigator.clipboard.writeText(finalText);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setError("Could not copy. Select the text and copy it manually.");
    }
  }

  const [statusLabel, statusClass] = STATUS_STYLE[report.status] || STATUS_STYLE.yellow;
  const s = report.summary || { total: issues.length, high: 0, medium: 0, low: 0 };

  return (
    <main className="mx-auto max-w-5xl px-6 py-12">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="font-display text-4xl font-semibold text-burgundy">Report</h1>
        <span className={`rounded-full px-3 py-1 text-sm font-medium ${statusClass}`}>{statusLabel}</span>
        <span className="text-sm text-ink/70">
          {s.total} issue{s.total === 1 ? "" : "s"} · {s.high} high · {s.medium} medium · {s.low} low
        </span>
      </div>
      {USE_MOCK && (
        <p className="mt-3 rounded-lg border border-latte/70 bg-mocha/50 p-3 text-sm">
          Demo data: the backend is not connected yet, so this is the sample response from the API contract.
        </p>
      )}
      {intent && <p className="mt-2 text-ink/70">Goal: {intent}</p>}
      {report.ai_used === false && (
        <p className="mt-3 rounded-lg bg-amber-50 p-3 text-sm text-amber-900">
          The AI check was unavailable, so only rule checks ran. Review the text yourself too.
        </p>
      )}
      {report.pii_masked && (
        <p className="mt-3 rounded-lg bg-stone-100 p-3 text-sm">Private details in your text were masked.</p>
      )}

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <section className="glass rounded-2xl p-5">
          <h2 className="eyebrow mb-3">Before</h2>
          <p style={textStyle}>{show(before)}</p>
        </section>
        <section className="glass rounded-2xl p-5">
          <h2 className="eyebrow mb-3">After</h2>
          <p style={textStyle}>{show(after)}</p>
          <div className="mt-4 flex flex-wrap items-center gap-4">
            <button onClick={copy} className="btn-neon rounded-lg px-5 py-2 text-sm">
              {copied ? "Copied" : "Copy final text"}
            </button>
            <span className="text-xs text-ink/70">
              <mark className="rounded bg-green-200 px-1">brand rule fix</mark>{" "}
              <mark className="rounded bg-amber-200 px-1">approved fact</mark>
            </span>
          </div>
        </section>
      </div>

      <section className="mt-10 space-y-4">
        <h2 className="eyebrow">Issues</h2>
        {issues.length === 0 && <p>No issues found. Your text follows the brand rules.</p>}
        {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
        {issues.map((i) => {
          const st = statusOf(i);
          const rep = replacementOf(i);
          return (
            <article key={i.id} className="glass space-y-3 rounded-2xl p-5">
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className={`rounded-full px-2 py-0.5 ${SEV_STYLE[i.severity]}`}>{i.severity}</span>
                <span className="rounded-full bg-mocha px-2 py-0.5">{TYPE_LABEL[i.type] || i.type}</span>
                {i.needs_human && <span className="rounded-full bg-red-100 px-2 py-0.5 text-red-800">Needs human review</span>}
                <span className="text-ink/60">{Math.round((i.confidence ?? 0) * 100)}% confident</span>
              </div>
              <p>
                <span className="text-red-700 line-through">{i.original_text}</span>
                {rep && (
                  <>
                    {" → "}
                    <span className="font-medium text-green-800">{rep}</span>
                  </>
                )}
              </p>
              <p className="text-sm">{i.reason}</p>
              {i.source ? (
                <p className="text-xs text-ink/70">
                  Source {i.source.id} ({i.source.kind}): {i.source.excerpt}
                </p>
              ) : (
                <p className="text-xs text-ink/70">No source found. A person needs to judge this one.</p>
              )}

              {editing === i.id ? (
                <div className="flex gap-2">
                  <input
                    className="flex-1 rounded-lg border border-latte/70 bg-white/70 px-3 py-1.5"
                    value={edits[i.id] ?? ""}
                    onChange={(e) => setEdits((x) => ({ ...x, [i.id]: e.target.value }))}
                  />
                  <button className="btn-neon rounded-lg px-4 text-sm" onClick={() => { act(i, "edit", edits[i.id] ?? ""); setEditing(null); }}>
                    Save
                  </button>
                </div>
              ) : (
                <div className="flex gap-2">
                  <button className={`chip ${st === "accepted" ? "chip-active" : ""}`} onClick={() => act(i, "accept")}>
                    Accept fix
                  </button>
                  <button
                    className={`chip ${st === "edited" ? "chip-active" : ""}`}
                    onClick={() => { setEdits((x) => ({ ...x, [i.id]: x[i.id] ?? i.suggested_fix ?? "" })); setEditing(i.id); }}
                  >
                    Edit
                  </button>
                  <button className={`chip ${st === "disputed" ? "chip-active" : ""}`} onClick={() => act(i, "dispute")}>
                    Dispute
                  </button>
                </div>
              )}
            </article>
          );
        })}
      </section>

      <Link to="/analyze" className="mt-10 inline-block text-sm text-burgundy underline">
        Check another text
      </Link>
    </main>
  );
}