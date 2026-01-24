export const DOCUMENT_STATUS = {
  UPLOADED: "uploaded",
  IN_PROCESSING: "in_processing",
  SUCCESS: "success",
  FAILED: "failed",
} as const;

export type DocumentStatus = typeof DOCUMENT_STATUS[keyof typeof DOCUMENT_STATUS];
