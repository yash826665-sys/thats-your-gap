"use client";

import { motion } from "framer-motion";

export function DimensionMeter({ label, value }: { label: string; value: number }) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className="py-3 border-b hairline border-t-0 last:border-b-0">
      <div className="flex items-baseline justify-between mb-2">
        <span className="text-sm text-ink">{label}</span>
        <span className="font-mono text-sm text-ink-muted">{clamped}</span>
      </div>
      <div className="h-[3px] w-full bg-hairline">
        <motion.div
          className="h-[3px] bg-scan"
          initial={{ width: 0 }}
          animate={{ width: `${clamped}%` }}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        />
      </div>
    </div>
  );
}
