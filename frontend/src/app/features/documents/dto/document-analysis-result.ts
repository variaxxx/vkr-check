export interface DocumentAnalysisResult {
  metadata: {
    timestamp: Date;
  };
  info: {
    students: string[];
    theme: string;
  };
  analysis: AnalysisPoint[];
  summary: {
    average_score: number;
    compliance_percentage: number;
    total_points_analyzed: number;
  };
  signs_verification: {
    signs_status_code: boolean;
  };
  evaluations: EvaluationItem[];
}

export interface EvaluationItem {
  section: EvaluationSection;
  score: number;
  details: string;
  if_links_exists?: boolean;
}

export interface AnalysisPoint {
  task_point: string;
  score: number;
  justification: string;
}

export type EvaluationSection = "introduction" | "application" | "literature" | "conclusion";
