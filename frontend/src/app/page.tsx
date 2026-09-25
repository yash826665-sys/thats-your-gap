"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ScanLine, FileSearch, Sparkles, ShieldCheck } from "lucide-react";

const steps = [
  {
    icon: <FileSearch size={20} />,
    title: "Upload your profile",
    body: "Your LinkedIn PDF export and your resume. Both stay on our server only for the duration of the analysis.",
  },
  {
    icon: <ScanLine size={20} />,
    title: "We analyze your evidence",
    body: "We compare what you claim against what you can actually demonstrate — across both documents.",
  },
  {
    icon: <Sparkles size={20} />,
    title: "Get your That's Your Gap",
    body: "A clear read on your positioning, your strongest signal, and exactly what to fix first.",
  },
];

export default function LandingPage() {
  return (
    <main>
      {/* Hero */}
      <section className="scan-texture relative overflow-hidden">
        <div className="max-w-5xl mx-auto px-6 pt-28 pb-24 grid md:grid-cols-[1.3fr_1fr] gap-16 items-end">
          <div>
            <p className="text-xs uppercase tracking-[0.14em] text-ink-faint mb-6">That's Your Gap</p>
            <motion.h1
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
              className="font-display text-5xl md:text-6xl leading-[1.05] text-ink"
            >
              See how the internet sees your career.
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
              className="mt-6 text-lg text-ink-muted max-w-lg leading-relaxed"
            >
              Upload your LinkedIn profile and resume. That's Your Gap finds the signals, gaps,
              inconsistencies, and blind spots that may be hiding in your profile.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
              className="mt-10 flex flex-col sm:flex-row sm:items-center gap-4"
            >
              <Link
                href="/analyze"
                className="inline-flex items-center justify-center bg-ink text-bg px-7 py-3.5 text-sm font-medium hover:bg-scan transition-colors"
              >
                Reveal My Gaps →
              </Link>
              <p className="text-xs text-ink-faint flex items-center gap-1.5">
                <ShieldCheck size={14} />
                No LinkedIn password. No scraping. Upload your own profile PDF.
              </p>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.3 }}
            className="hidden md:block"
          >
            <svg viewBox="0 0 220 260" width="100%" aria-hidden="true">
              <rect x="1" y="1" width="218" height="258" fill="none" stroke="#262E3A" />
              {Array.from({ length: 9 }).map((_, i) => (
                <line
                  key={i}
                  x1="1"
                  x2="219"
                  y1={30 + i * 25}
                  y2={30 + i * 25}
                  stroke="#1B222C"
                  strokeWidth="1"
                />
              ))}
              <motion.line
                x1="1"
                x2="219"
                y1="130"
                y2="130"
                stroke="#6FE3FF"
                strokeWidth="1.5"
                initial={{ y1: 20, y2: 20 }}
                animate={{ y1: [20, 240, 20], y2: [20, 240, 20] }}
                transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
              />
              <text x="16" y="200" fontFamily="var(--font-plex-mono)" fontSize="11" fill="#5A6472">
                POSITIONING · EVIDENCE
              </text>
              <text x="16" y="216" fontFamily="var(--font-plex-mono)" fontSize="11" fill="#5A6472">
                CLARITY · IMPACT
              </text>
            </svg>
          </motion.div>
        </div>
      </section>

      {/* How it works */}
      <section className="border-t hairline">
        <div className="max-w-5xl mx-auto px-6 py-24">
          <h2 className="font-display text-2xl text-ink mb-12">How it works</h2>
          <div className="grid md:grid-cols-3 gap-10">
            {steps.map((step, i) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div className="text-scan mb-4">{step.icon}</div>
                <h3 className="text-ink font-medium mb-2">{step.title}</h3>
                <p className="text-sm text-ink-muted leading-relaxed">{step.body}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t hairline">
        <div className="max-w-5xl mx-auto px-6 py-10 flex flex-col sm:flex-row justify-between gap-4 text-xs text-ink-faint">
          <p>That's Your Gap is a diagnostic tool, not a hiring prediction.</p>
          <p>Your documents are never stored beyond your session.</p>
        </div>
      </footer>
    </main>
  );
}
