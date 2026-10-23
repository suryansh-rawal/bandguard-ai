import { Link } from "react-router-dom";

const markBad = "rounded bg-burgundy/15 px-1 text-burgundy";
const markGood = "rounded bg-emerald-700/15 px-1 text-emerald-900";

const PRINCIPLES = [
  {
    title: "Every flag has a source",
    text: "Each issue points to the Brand Kit rule or approved fact behind it. When there is no source, we say a person needs to decide instead of guessing.",
  },
  {
    title: "Fixes keep your meaning",
    text: "Suggested wording stays close to what you wanted to say. You accept, edit or dispute each one. Nothing changes on its own.",
  },
  {
    title: "People stay in control",
    text: "Risky claims are marked for a human reviewer, and the final decision is always theirs.",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <span className="font-display text-2xl font-semibold text-burgundy">BrandGuard AI</span>
        <Link
          to="/analyze"
          className="rounded-full border border-burgundy px-5 py-2 text-sm text-burgundy transition hover:bg-burgundy hover:text-ivory"
        >
          Check content
        </Link>
      </header>

      <main>
        {/* Hero */}
        <section className="mx-auto grid max-w-6xl items-center gap-12 px-6 pb-20 pt-10 lg:grid-cols-2">
          <div>
            <h1 className="font-display text-5xl font-semibold leading-[1.05] md:text-6xl">
              Fix brand mistakes <span className="gradient-text">before</span> they are published
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-8 text-ink/70">
              BrandGuard AI checks your content against your approved guidelines and facts, explains
              every issue with its source, and suggests fixes that keep your message.
            </p>
            <div className="mt-9 flex flex-wrap items-center gap-6">
              <Link to="/analyze" className="btn-neon rounded-full px-8 py-4 text-sm">
                Check your content
              </Link>
              <a href="#why" className="text-sm text-burgundy underline-offset-4 hover:underline">
                Why you can trust the results
              </a>
            </div>
          </div>

          {/* Before / after sample */}
          <div className="glass flex flex-col gap-5 rounded-3xl p-6 sm:p-7">
            <div className="flex items-center justify-between">
              <h2 className="eyebrow">Sample report</h2>
              <span className="rounded-full bg-burgundy/10 px-3 py-1 text-xs text-burgundy">
                2 issues found
              </span>
            </div>

            <div>
              <p className="mb-2 text-xs font-medium text-ink/55">Before</p>
              <p className="rounded-xl bg-white/70 p-4 text-sm leading-7">
                “ABC App is the <mark className={markBad}>number one</mark> app in the world and
                supports <mark className={markBad}>25 languages</mark>.”
              </p>
            </div>

            <div className="flex flex-col gap-2 text-sm">
              <div className="rounded-xl border border-latte/50 bg-white/60 p-3.5">
                <p className="font-semibold text-burgundy">Superlative needs evidence</p>
                <p className="mt-0.5 text-ink/65">
                  “Number one” has no approved source in the Brand Kit (rule R-02).
                </p>
              </div>
              <div className="rounded-xl border border-latte/50 bg-white/60 p-3.5">
                <p className="font-semibold text-burgundy">Fact mismatch</p>
                <p className="mt-0.5 text-ink/65">
                  The approved fact says the app supports 10 languages, not 25 (F-01).
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 text-xs text-ink/50">
              <span className="h-px flex-1 bg-latte/50" />
              You review each fix
              <span className="h-px flex-1 bg-latte/50" />
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between">
                <p className="text-xs font-medium text-ink/55">After</p>
                <span className="rounded-full bg-emerald-700/10 px-3 py-1 text-xs text-emerald-900">
                  Matches the Brand Kit
                </span>
              </div>
              <p className="rounded-xl border border-emerald-700/25 bg-emerald-700/5 p-4 text-sm leading-7">
                “ABC App <mark className={markGood}>helps teams create reports quickly</mark> and
                supports <mark className={markGood}>10 languages</mark>.”
              </p>
              <p className="mt-2 text-xs text-ink/50">
                Sample content from a fictional company, ABC Technologies.
              </p>
            </div>
          </div>
        </section>

        {/* Principles */}
        <section id="why" className="mx-auto max-w-6xl px-6 pb-24">
          <h2 className="font-display text-3xl font-semibold md:text-4xl">
            Results you can check, and decisions you still make
          </h2>
          <div className="mt-8 grid gap-x-10 gap-y-8 md:grid-cols-3">
            {PRINCIPLES.map((p) => (
              <div key={p.title} className="border-t border-burgundy/40 pt-5">
                <h3 className="font-display text-xl font-semibold text-burgundy">{p.title}</h3>
                <p className="mt-2 text-sm leading-7 text-ink/70">{p.text}</p>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-latte/40">
        <p className="mx-auto max-w-6xl px-6 py-6 text-xs leading-6 text-ink/55">
          AI-assisted review. Suggestions are never applied automatically. Demo data only.
        </p>
      </footer>
    </div>
  );
}