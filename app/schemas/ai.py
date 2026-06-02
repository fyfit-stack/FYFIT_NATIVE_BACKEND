from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import TimestampedSchema


class AISuggestionRequest(BaseModel):
    suggestion_type: str
    force_refresh: bool = False


class AISuggestionSchema(TimestampedSchema):
    user_id: UUID
    suggestion_type: str
    title: str
    body: str
    model_provider: str | None = None
    model_name: str | None = None
    input_hash: str
    evidence: dict | None = None
    expires_at: datetime | None = None

