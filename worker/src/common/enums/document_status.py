import enum


class DocumentStatus(enum.Enum):
    UPLOADED = "uploaded"
    IN_PROCESSING = "in_processing"
    FAILED = "failed"
    APPROVED = "approved"
    REJECTED = "rejected"
