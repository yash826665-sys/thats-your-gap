"use client";

import { motion } from "framer-motion";

/**
 * A diagnostic arc gauge, deliberately not a generic circular progress ring:
 * it reads left-to-right like a meter on an instrument panel, echoing the
 * "diagnostic scan" visual language used across the results report.
 */
export function ScoreDial({ score, label }: { score: number; label: string }) {
  const clamped = Math.max(0, Math.min(100, score));
  const radius = 84;
  const circumference = Math.PI * radius; // half circle
  const offset = circumference * (1 - clamped / 100);

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 200 116" width="220" height="128" role="img" aria-label={`${label}: ${clamped} out of 100`}>
        <path
          d="M 16 100 A 84 84 0 0 1 184 100"
          fill="none"
          stroke="#262E3A"
          strokeWidth="10"
          strokeLinecap="round"
        />
        <motion.path
          d="M 16 100 A 84 84 0 0 1 184 100"
          fill="none"
          stroke="#6FE3FF"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
        />
        <text
          x="100"
          y="86"
          textAnchor="middle"
          className="font-mono"
          fontSize="42"
          fill="#ECEEF1"
        >
          {clamped}
        </text>
      </svg>
      <p className="text-sm text-ink-muted -mt-2">{label}</p>
    </div>
  );
}
