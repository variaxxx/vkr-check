export interface DocumentAnalysisResult {
  metadata: {
    timestamp: Date;
  };
  info: {
    students: string[];
    theme: string;
  };
  summary: {
    average_score: number;
    compliance_percentage: number;
    total_points_analyzed: number;
  };
  signs_verification: {
    signs_status_code: boolean;
  };
  analysis: AnalysisPoint[];
  evaluations: EvaluationItem[];
}

export interface AnalysisPoint {
  task_point: string;
  score: number;
  justification: string;
}

export interface EvaluationItem {
  found: boolean;
  section: EvaluationSection;
  score: number;
  details: string;
  tech_details: {
    if_links_exists?: boolean;
  };
}

export type EvaluationSection = "introduction" | "application" | "literature" | "conclusion" | "annotation";
