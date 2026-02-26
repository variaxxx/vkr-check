export const DOCUMENT_STATUS = {
  UPLOADED: "uploaded",
  IN_PROCESSING: "in_processing",
  FAILED: "failed",
  APPROVED: "approved",
  REJECTED: "rejected",
} as const;

export type DocumentStatus = typeof DOCUMENT_STATUS[keyof typeof DOCUMENT_STATUS];
