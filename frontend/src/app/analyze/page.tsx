"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, AlertCircle } from "lucide-react";
import { UploadSlot } from "@/components/UploadSlot";
import { AnalyzingState } from "@/components/AnalyzingState";
import { ResultsReport } from "@/components/ResultsReport";
import { analyzeCareerProfile, ApiError } from "@/lib/api";
import type { CareerXRayResult } from "@/lib/types";

type Phase = "upload" | "analyzing" | "results";

export default function AnalyzePage() {
  const [phase, setPhase] = useState<Phase>("upload");
  const [linkedinPdf, setLinkedinPdf] = useState<File | null>(null);
  const [resumePdf, setResumePdf] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CareerXRayResult | null>(null);

  const canSubmit = Boolean(linkedinPdf && resumePdf);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!linkedinPdf || !resumePdf) return;

    setError(null);
    setPhase("analyzing");

    try {
      const analysis = await analyzeCareerProfile({
        linkedinPdf,
        resumePdf,
        targetRole: targetRole.trim() || undefined,
        jobDescription: jobDescription.trim() || undefined,
      });
      setResult(analysis);
      setPhase("results");
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Something unexpected happened. Please try again.";
      setError(message);
      setPhase("upload");
    }
  }

  if (phase === "analyzing") {
    return <AnalyzingState />;
  }

  if (phase === "results" && result) {
    return <ResultsReport result={result} />;
  }

  return (
    <main className="max-w-xl mx-auto px-6 py-16">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm text-ink-faint hover:text-ink transition-colors mb-10"
      >
        <ArrowLeft size={14} /> Back
      </Link>

      <h1 className="font-display text-3xl text-ink mb-2">Upload your profile</h1>
      <p className="text-sm text-ink-muted mb-10">
        We'll read both documents and never store them beyond this session.
      </p>

      {error && (
        <div className="mb-8 border border-gap/40 bg-gap/5 px-4 py-3 flex items-start gap-2.5 text-sm text-ink">
          <AlertCircle size={16} className="text-gap shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        <UploadSlot
          label="LinkedIn PDF"
          hint="Profile → Resources → Save to PDF"
          file={linkedinPdf}
          onChange={setLinkedinPdf}
        />
        <UploadSlot label="Resume PDF" hint="Required" file={resumePdf} onChange={setResumePdf} />

        <div>
          <label htmlFor="target-role" className="text-sm text-ink block mb-2">
            Target role <span className="text-ink-faint">(optional)</span>
          </label>
          <input
            id="target-role"
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. Data Analyst Intern"
            maxLength={200}
            className="w-full bg-panel border border-hairline px-4 py-3 text-sm text-ink placeholder:text-ink-faint focus:border-scan outline-none transition-colors"
          />
        </div>

        <div>
          <label htmlFor="job-description" className="text-sm text-ink block mb-2">
            Job description <span className="text-ink-faint">(optional)</span>
          </label>
          <textarea
            id="job-description"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description here"
            rows={6}
            maxLength={8000}
            className="w-full bg-panel border border-hairline px-4 py-3 text-sm text-ink placeholder:text-ink-faint focus:border-scan outline-none transition-colors resize-y"
          />
        </div>

        <button
          type="submit"
          disabled={!canSubmit}
          className="w-full bg-ink text-bg py-3.5 text-sm font-medium hover:bg-scan transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Reveal My Gaps →
        </button>
      </form>
    </main>
  );
}
