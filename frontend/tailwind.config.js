import { useEffect, useState } from "react";

/**
 * Premium SaaS hero section.
 *
 * Built on top of the brand indigo scale already in tailwind.config.js
 * (brand.50 / 100 / 500 / 600 / 700). A few extra tones are used as
 * arbitrary Tailwind values below — if you want them as named tokens,
 * add this to your config's `colors.brand` block:
 *
 *   800: "#332e7a", 900: "#1f1b4d", 950: "#100e2e",
 *   glow: "#8b7ff0", ember: "#f2b84b"
 *
 * Fonts: this assumes Sora (display), Inter (body) and JetBrains Mono
 * (data chips) are loaded. Add to your index.html <head>:
 *
 *   <link rel="preconnect" href="https://fonts.googleapis.com">
 *   <link href="https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
 */

const NAV_LINKS = ["Product", "Pricing", "Docs", "Company"];

const FEATURES = [
  {
    title: "Real-time ingestion",
    body: "Stream millions of events a second with sub-100ms end-to-end latency.",
    icon: (
      <path d="M13 2 3 14h7l-1 8 10-12h-7l1-8Z" strokeWidth="1.6" strokeLinejoin="round" />
    ),
  },
  {
    title: "Model-aware routing",
    body: "Traffic is scored and routed by an internal model, not static rules.",
    icon: (
      <>
        <circle cx="12" cy="5" r="2.4" strokeWidth="1.6" />
        <circle cx="5" cy="19" r="2.4" strokeWidth="1.6" />
        <circle cx="19" cy="19" r="2.4" strokeWidth="1.6" />
        <path d="M12 7.4V13m0 0-5.3 3.6M12 13l5.3 3.6" strokeWidth="1.6" strokeLinecap="round" />
      </>
    ),
  },
  {
    title: "Audit-grade trails",
    body: "Every decision is logged, signed, and replayable for compliance review.",
    icon: (
      <>
        <path d="M6 3h9l4 4v14H6z" strokeWidth="1.6" strokeLinejoin="round" />
        <path d="M9.5 12h6M9.5 15.5h6M9.5 8.5h3" strokeWidth="1.6" strokeLinecap="round" />
      </>
    ),
  },
];

function AuroraField() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute -top-40 -left-32 h-[32rem] w-[32rem] rounded-full bg-brand-600/40 blur-[120px] animate-drift-slow" />
      <div className="absolute top-10 right-[-10rem] h-[28rem] w-[28rem] rounded-full bg-[#8b7ff0]/30 blur-[110px] animate-drift-slower" />
      <div className="absolute bottom-[-14rem] left-1/3 h-[26rem] w-[26rem] rounded-full bg-[#f2b84b]/20 blur-[130px] animate-drift-slow" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(16,14,46,0)_0%,#0a0a14_75%)]" />
    </div>
  );
}

function DashboardPreview() {
  const bars = [38, 62, 51, 84, 46, 70, 95, 58];
  return (
    <div className="relative [perspective:1600px]">
      <div className="[transform:rotateY(-10deg)_rotateX(4deg)] transition-transform duration-700 hover:[transform:rotateY(-4deg)_rotateX(2deg)]">
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur-xl shadow-[0_40px_100px_-20px_rgba(79,70,229,0.45)] p-5">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-[#f2b84b]" />
              <span className="font-mono text-[11px] tracking-wide text-white/50">
                LIVE · pipeline-04
              </span>
            </div>
            <span className="font-mono text-[11px] text-brand-100/70">99.98% uptime</span>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-6">
            {[
              ["Throughput", "482k/s"],
              ["P99 latency", "84ms"],
              ["Error rate", "0.02%"],
            ].map(([label, value]) => (
              <div
                key={label}
                className="rounded-xl border border-white/10 bg-white/[0.03] px-3 py-3"
              >
                <p className="font-mono text-[10px] uppercase tracking-wider text-white/40 mb-1">
                  {label}
                </p>
                <p className="font-display text-lg font-semibold text-white">{value}</p>
              </div>
            ))}
          </div>

          <div className="flex items-end gap-2 h-28">
            {bars.map((h, i) => (
              <div
                key={i}
                className="flex-1 rounded-t-md bg-gradient-to-t from-brand-600 via-brand-500 to-[#8b7ff0]"
                style={{ height: `${h}%`, opacity: 0.55 + (i / bars.length) * 0.45 }}
              />
            ))}
          </div>
        </div>

        <div className="absolute -bottom-6 -right-6 rounded-xl border border-white/10 bg-[#12121f]/90 backdrop-blur-xl px-4 py-3 shadow-xl">
          <p className="font-mono text-[10px] uppercase tracking-wider text-white/40">Anomalies</p>
          <p className="font-display text-2xl font-semibold text-[#f2b84b]">0</p>
        </div>
      </div>
    </div>
  );
}

export default function PremiumHero() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="relative min-h-screen bg-[#0a0a14] font-sans text-white/90 overflow-hidden">
      <style>{`
        .font-display { font-family: "Sora", ui-sans-serif, system-ui, sans-serif; }
        .font-sans { font-family: "Inter", ui-sans-serif, system-ui, sans-serif; }
        .font-mono { font-family: "JetBrains Mono", ui-monospace, monospace; }
        @keyframes driftSlow {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(30px, -20px) scale(1.06); }
        }
        @keyframes driftSlower {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(-24px, 26px) scale(1.08); }
        }
        .animate-drift-slow { animation: driftSlow 14s ease-in-out infinite; }
        .animate-drift-slower { animation: driftSlower 19s ease-in-out infinite; }
        @media (prefers-reduced-motion: reduce) {
          .animate-drift-slow, .animate-drift-slower { animation: none; }
        }
      `}</style>

      <AuroraField />

      {/* Nav */}
      <header
        className={`sticky top-0 z-20 transition-colors duration-300 ${
          scrolled ? "bg-[#0a0a14]/80 backdrop-blur-lg border-b border-white/5" : ""
        }`}
      >
        <div className="mx-auto max-w-6xl px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="h-7 w-7 rounded-lg bg-gradient-to-br from-brand-500 to-[#8b7ff0]" />
            <span className="font-display font-semibold tracking-tight text-white">Aether</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm text-white/60">
            {NAV_LINKS.map((link) => (
              <a key={link} href="#" className="hover:text-white transition-colors">
                {link}
              </a>
            ))}
          </nav>
          <div className="flex items-center gap-3">
            <a href="#" className="hidden sm:block text-sm text-white/60 hover:text-white transition-colors">
              Sign in
            </a>
            <a
              href="#"
              className="rounded-lg bg-white text-[#0a0a14] text-sm font-medium px-4 py-2 hover:bg-white/90 transition-colors"
            >
              Start free
            </a>
          </div>
        </div>
      </header>

      {/* Hero */}
      <main className="relative mx-auto max-w-6xl px-6 pt-16 pb-28 grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 mb-6">
            <span className="h-1.5 w-1.5 rounded-full bg-[#f2b84b]" />
            <span className="font-mono text-[11px] tracking-wide text-white/60">
              v3.2 · now with anomaly forecasting
            </span>
          </div>

          <h1 className="font-display text-[2.75rem] leading-[1.08] sm:text-6xl font-semibold tracking-tight text-white mb-6">
            Infrastructure that
            <br />
            <span className="bg-gradient-to-r from-brand-100 via-[#c9c2ff] to-[#f2b84b] bg-clip-text text-transparent">
              anticipates failure
            </span>
          </h1>

          <p className="text-lg text-white/55 max-w-md mb-9 leading-relaxed">
            Aether watches every request across your stack and routes around
            trouble before your on-call gets paged.
          </p>

          <div className="flex flex-wrap items-center gap-4 mb-12">
            <a
              href="#"
              className="rounded-lg bg-gradient-to-r from-brand-600 to-brand-500 px-6 py-3 text-sm font-medium text-white shadow-[0_8px_30px_-8px_rgba(99,102,241,0.7)] hover:brightness-110 transition"
            >
              Start free trial
            </a>
            <a
              href="#"
              className="rounded-lg border border-white/15 px-6 py-3 text-sm font-medium text-white/80 hover:bg-white/5 transition"
            >
              View live demo
            </a>
          </div>

          <div className="flex items-center gap-8 border-t border-white/10 pt-6">
            {[
              ["4.2B", "events routed / day"],
              ["230+", "teams in production"],
              ["<100ms", "p99 decision time"],
            ].map(([stat, label]) => (
              <div key={label}>
                <p className="font-display text-xl font-semibold text-white">{stat}</p>
                <p className="text-xs text-white/40 mt-0.5">{label}</p>
              </div>
            ))}
          </div>
        </div>

        <DashboardPreview />
      </main>

      {/* Feature strip */}
      <section className="relative mx-auto max-w-6xl px-6 pb-28">
        <div className="grid sm:grid-cols-3 gap-5">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl p-6 hover:bg-white/[0.05] transition-colors"
            >
              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                className="text-brand-100 mb-4"
              >
                {f.icon}
              </svg>
              <h3 className="font-display text-base font-semibold text-white mb-2">
                {f.title}
              </h3>
              <p className="text-sm text-white/50 leading-relaxed">{f.body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}