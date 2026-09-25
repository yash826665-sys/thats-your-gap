"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const STAGES = [
  "Reading your profile...",
  "Mapping your experience...",
  "Checking evidence...",
  "Comparing positioning...",
  "Finding blind spots...",
  "Building your That's Your Gap...",
];

/**
 * Cycles through descriptive stage copy on a timer while the real request
 * is in flight. This is honest about what's happening conceptually, but
 * does NOT claim a fake percentage or a fake completion time — the actual
 * completion is driven by the API call resolving, not this timer.
 */
export function AnalyzingState() {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStageIndex((i) => Math.min(i + 1, STAGES.length - 1));
    }, 2200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-6 text-center">
      <div className="relative w-12 h-12 mb-8">
        <div className="absolute inset-0 border border-hairline rounded-full" />
        <motion.div
          className="absolute inset-0 border border-transparent border-t-scan rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1.4, repeat: Infinity, ease: "linear" }}
        />
      </div>
      <AnimatePresence mode="wait">
        <motion.p
          key={stageIndex}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.3 }}
          className="font-display text-xl italic text-ink"
        >
          {STAGES[stageIndex]}
        </motion.p>
      </AnimatePresence>
      <p className="mt-3 text-sm text-ink-faint max-w-xs">
        This usually takes under a minute. We're reading your documents closely, not guessing.
      </p>
    </div>
  );
}
