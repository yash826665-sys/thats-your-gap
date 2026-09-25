"use client";

import { motion } from "framer-motion";
import { ScoreDial } from "./ScoreDial";
import { DimensionMeter } from "./DimensionMeter";
import type { CareerXRayResult } from "@/lib/types";
import { Sparkles, Eye, Compass, AlertTriangle, TrendingUp, GitCompare, Target, ArrowRight } from "lucide-react";

const fadeUp = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
};

function Section({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <motion.section
      {...fadeUp}
      transition={{ duration: 0.5 }}
      viewport={{ once: true, margin: "-80px" }}
      whileInView="animate"
      initial="initial"
      className="py-10 border-b hairline"
    >
      <div className="flex items-center gap-2.5 mb-4 text-ink-muted">
        {icon}
        <h2 className="font-display text-xl text-ink">{title}</h2>
      </div>
      {children}
    </motion.section>
  );
}

function Evidence({ items }: { items: string[] }) {
  if (!items?.length) return null;
  return (
    <ul className="mt-3 space-y-1.5">
      {items.map((item, i) => (
        <li key={i} className="text-xs text-ink-faint font-mono pl-4 -indent-4">
          — {item}
        </li>
      ))}
    </ul>
  );
}

export function ResultsReport({ result }: { result: CareerXRayResult }) {
  const {
    career_signal,
    dimensions,
    strongest_signal,
    biggest_blind_spot,
    positioning_diagnosis,
    evidence_gaps,
    impact_analysis,
    consistency_checks,
    target_role_match,
    next_three_moves,
  } = result;

  return (
    <div className="max-w-2xl mx-auto px-6 pb-32">
      {/* Header */}
      <div className="pt-16 pb-10 text-center">
        <p className="text-xs uppercase tracking-[0.14em] text-ink-faint mb-6">That's Your Gap</p>
        <ScoreDial score={career_signal} label="Career Signal" />
        <p className="mt-6 text-sm text-ink-faint max-w-sm mx-auto leading-relaxed">
          A diagnostic reading of how your profile currently comes across — not a prediction of
          hiring odds, ATS pass rates, or employability.
        </p>
      </div>

      {/* Dimensions */}
      <div className="pb-6">
        <DimensionMeter label="Positioning" value={dimensions.positioning} />
        <DimensionMeter label="Evidence" value={dimensions.evidence} />
        <DimensionMeter label="Clarity" value={dimensions.clarity} />
        <DimensionMeter label="Impact" value={dimensions.impact} />
        <DimensionMeter label="Role alignment" value={dimensions.role_alignment} />
      </div>

      <Section icon={<Sparkles size={18} />} title="Your strongest signal">
        <p className="text-ink leading-relaxed">{strongest_signal.insight}</p>
        <Evidence items={strongest_signal.evidence} />
      </Section>

      <Section icon={<Eye size={18} />} title="Your biggest blind spot">
        <p className="text-ink leading-relaxed">{biggest_blind_spot.insight}</p>
        <Evidence items={biggest_blind_spot.evidence} />
      </Section>

      <Section icon={<Compass size={18} />} title="How your profile is positioned">
        <p className="text-ink leading-relaxed">{positioning_diagnosis.insight}</p>
        <Evidence items={positioning_diagnosis.evidence} />
      </Section>

      {evidence_gaps?.length > 0 && (
        <Section icon={<AlertTriangle size={18} />} title="Evidence gaps">
          <div className="space-y-5">
            {evidence_gaps.map((gap, i) => (
              <div key={i}>
                <p className="text-ink">
                  <span className="text-ink-muted">{gap.claim}</span> — {gap.gap}
                </p>
                <Evidence items={gap.evidence} />
              </div>
            ))}
          </div>
        </Section>
      )}

      <Section icon={<TrendingUp size={18} />} title="Impact analysis">
        <p className="text-ink leading-relaxed">{impact_analysis.insight}</p>
        <Evidence items={impact_analysis.evidence} />
      </Section>

      {consistency_checks?.length > 0 && (
        <Section icon={<GitCompare size={18} />} title="LinkedIn vs. resume consistency">
          <div className="space-y-4">
            {consistency_checks.map((check, i) => (
              <div key={i} className="text-sm">
                <p className="text-ink-muted mb-1">{check.topic}</p>
                <p className="text-ink">{check.note}</p>
                {(check.linkedin_version || check.resume_version) && (
                  <div className="mt-1.5 grid grid-cols-2 gap-3 text-xs font-mono text-ink-faint">
                    <span>LinkedIn: {check.linkedin_version || "—"}</span>
                    <span>Resume: {check.resume_version || "—"}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {target_role_match && (
        <Section icon={<Target size={18} />} title="Target role match">
          <div className="space-y-6">
            {target_role_match.matched_strengths.length > 0 && (
              <div>
                <p className="text-xs uppercase tracking-wide text-ink-faint mb-2">Matched strengths</p>
                {target_role_match.matched_strengths.map((s, i) => (
                  <p key={i} className="text-ink leading-relaxed mb-1">
                    {s.insight}
                  </p>
                ))}
              </div>
            )}
            {target_role_match.missing_evidence.length > 0 && (
              <div>
                <p className="text-xs uppercase tracking-wide text-ink-faint mb-2">Missing evidence</p>
                {target_role_match.missing_evidence.map((s, i) => (
                  <p key={i} className="text-ink leading-relaxed mb-1">
                    {s.insight}
                  </p>
                ))}
              </div>
            )}
            {target_role_match.potential_gaps.length > 0 && (
              <div>
                <p className="text-xs uppercase tracking-wide text-ink-faint mb-2">Potential gaps</p>
                {target_role_match.potential_gaps.map((s, i) => (
                  <p key={i} className="text-ink leading-relaxed mb-1">
                    {s.insight}
                  </p>
                ))}
              </div>
            )}
            {target_role_match.recommended_changes.length > 0 && (
              <div>
                <p className="text-xs uppercase tracking-wide text-ink-faint mb-2">Recommended changes</p>
                <ul className="space-y-1.5">
                  {target_role_match.recommended_changes.map((c, i) => (
                    <li key={i} className="text-ink leading-relaxed">
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Section>
      )}

      {/* Next 3 moves */}
      <section className="pt-10">
        <h2 className="font-display text-2xl text-ink mb-6">Your next three moves</h2>
        <div className="space-y-6">
          {next_three_moves.map((move, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="flex gap-4"
            >
              <span className="font-mono text-scan text-sm pt-1">{String(i + 1).padStart(2, "0")}</span>
              <div>
                <p className="text-ink leading-relaxed">{move.recommendation}</p>
                <p className="text-sm text-ink-faint mt-1.5 leading-relaxed">{move.reason}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      <div className="pt-16 flex justify-center">
        <a
          href="/analyze"
          className="inline-flex items-center gap-2 text-sm text-ink-muted hover:text-ink transition-colors"
        >
          Run another That's Your Gap <ArrowRight size={14} />
        </a>
      </div>
    </div>
  );
}
