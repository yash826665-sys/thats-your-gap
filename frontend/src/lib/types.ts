export interface EvidencedInsight {
  insight: string;
  evidence: string[];
}

export interface Dimensions {
  positioning: number;
  evidence: number;
  clarity: number;
  impact: number;
  role_alignment: number;
}

export interface EvidenceGap {
  claim: string;
  gap: string;
  evidence: string[];
}

export interface ConsistencyCheck {
  topic: string;
  linkedin_version: string;
  resume_version: string;
  note: string;
}

export interface TargetRoleMatch {
  matched_strengths: EvidencedInsight[];
  missing_evidence: EvidencedInsight[];
  potential_gaps: EvidencedInsight[];
  recommended_changes: string[];
}

export interface NextMove {
  recommendation: string;
  reason: string;
}

export interface CareerXRayResult {
  career_signal: number;
  dimensions: Dimensions;
  strongest_signal: EvidencedInsight;
  biggest_blind_spot: EvidencedInsight;
  positioning_diagnosis: EvidencedInsight;
  evidence_gaps: EvidenceGap[];
  impact_analysis: EvidencedInsight;
  consistency_checks: ConsistencyCheck[];
  target_role_match: TargetRoleMatch | null;
  next_three_moves: NextMove[];
}

export interface ApiErrorResponse {
  detail: string;
}
