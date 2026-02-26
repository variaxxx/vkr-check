import { DocumentStatus } from "../../../shared/enums";
import { DocumentAuthor } from "./document-author";

export interface DocumentShortResponse {
  id: string;
  created_at: Date;
  original_name: string;
  status: DocumentStatus;
  authors: DocumentAuthor[] | null;
  topic: string | null;
  score: number | null;
}
