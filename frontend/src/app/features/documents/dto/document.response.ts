import { DocumentStatus } from "../../../shared/enums";
import { DocumentAnalysisResult } from "./document-analysis-result";

export interface DocumentResponse {
  id: string;
  created_at: Date;
  processed_at: Date | null;
  original_name: string;
  status: DocumentStatus;
  authors: string[] | null;
  topic: string | null;
  score: number | null;
  result: DocumentAnalysisResult | null;
}
