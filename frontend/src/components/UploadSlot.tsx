"use client";

import { useRef, useState, useCallback } from "react";
import { FileText, Upload, X, AlertCircle } from "lucide-react";

const MAX_SIZE_MB = 10;

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function UploadSlot({
  label,
  hint,
  file,
  onChange,
}: {
  label: string;
  hint: string;
  file: File | null;
  onChange: (file: File | null) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateAndSet = useCallback(
    (candidate: File | undefined) => {
      if (!candidate) return;
      if (candidate.type !== "application/pdf") {
        setError("Please upload a PDF file.");
        return;
      }
      if (candidate.size > MAX_SIZE_MB * 1024 * 1024) {
        setError(`File is too large. Max size is ${MAX_SIZE_MB}MB.`);
        return;
      }
      setError(null);
      onChange(candidate);
    },
    [onChange]
  );

  return (
    <div>
      <div className="flex items-baseline justify-between mb-2">
        <label className="text-sm text-ink">{label}</label>
        <span className="text-xs text-ink-faint">{hint}</span>
      </div>

      {!file ? (
        <div
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
          }}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragging(false);
            validateAndSet(e.dataTransfer.files?.[0]);
          }}
          role="button"
          tabIndex={0}
          className={`border ${
            isDragging ? "border-scan bg-panel-raised" : "border-hairline"
          } hover:border-ink-faint transition-colors cursor-pointer px-5 py-8 flex flex-col items-center justify-center gap-2 text-center`}
        >
          <Upload size={20} className="text-ink-muted" />
          <p className="text-sm text-ink-muted">
            Drop your PDF here, or <span className="text-scan">browse</span>
          </p>
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf"
            className="hidden"
            onChange={(e) => validateAndSet(e.target.files?.[0])}
          />
        </div>
      ) : (
        <div className="border border-hairline px-4 py-3 flex items-center gap-3 bg-panel">
          <FileText size={18} className="text-scan shrink-0" />
          <div className="min-w-0 flex-1">
            <p className="text-sm text-ink truncate">{file.name}</p>
            <p className="text-xs text-ink-faint">{formatSize(file.size)}</p>
          </div>
          <button
            type="button"
            onClick={() => onChange(null)}
            aria-label={`Remove ${label}`}
            className="text-ink-faint hover:text-ink transition-colors p-1"
          >
            <X size={16} />
          </button>
        </div>
      )}

      {error && (
        <p className="mt-2 text-xs text-gap flex items-center gap-1.5">
          <AlertCircle size={13} />
          {error}
        </p>
      )}
    </div>
  );
}
