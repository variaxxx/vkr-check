import { DocumentStatus } from "../../../shared/enums";

export interface DocumentInfoResponse {
  id: string;
  created_at: Date;
  processed_at?: Date;
  original_name: string;
  status: DocumentStatus;
  authors?: string[];
  result?: string;
}
