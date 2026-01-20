import uuid


def normalize_uuid(
    id: uuid.UUID | str,
) -> uuid.UUID:
    return uuid.UUID(id) if isinstance(id, str) else id
