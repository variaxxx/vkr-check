import enum


class DocumentStatus(enum.Enum):
    UPLOADED = "uploaded"
    IN_PROCESSING = "in_processing"
    SUCCESS = "success"
    FAILED = "failed"
