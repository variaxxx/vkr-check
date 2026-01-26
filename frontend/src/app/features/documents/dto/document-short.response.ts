import { DocumentStatus } from "../../../shared/enums";

export interface DocumentShortResponse {
  id: string;
  created_at: Date;
  original_name: string;
  status: DocumentStatus;
  authors: string[] | null;
  topic: string | null;
  score: number | null;
}
