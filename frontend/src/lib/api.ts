import type { CareerXRayResult } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

export async function analyzeCareerProfile(params: {
  linkedinPdf: File;
  resumePdf: File;
  targetRole?: string;
  jobDescription?: string;
  signal?: AbortSignal;
}): Promise<CareerXRayResult> {
  const formData = new FormData();
  formData.append("linkedin_pdf", params.linkedinPdf);
  formData.append("resume_pdf", params.resumePdf);
  if (params.targetRole) formData.append("target_role", params.targetRole);
  if (params.jobDescription) formData.append("job_description", params.jobDescription);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: "POST",
      body: formData,
      signal: params.signal,
    });
  } catch (err) {
    throw new ApiError(
      "We couldn't reach the analysis server. Check your connection and try again.",
      0
    );
  }

  if (!response.ok) {
    let message = "Something went wrong while analyzing your profile.";
    try {
      const errorBody = await response.json();
      if (errorBody?.detail) message = errorBody.detail;
    } catch {
      // Response wasn't JSON — keep the default message. Never surface raw body.
    }
    throw new ApiError(message, response.status);
  }

  return (await response.json()) as CareerXRayResult;
}
