import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Boolean, Float, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class AISuggestion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ai_suggestions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    insight_type: Mapped[str] = mapped_column(String(30), index=True)
    title: Mapped[str] = mapped_column(String(120))
    suggestion: Mapped[str] = mapped_column(Text)
    action_hint: Mapped[str | None] = mapped_column(String(255))
    priority: Mapped[int | None] = mapped_column(SmallInteger, default=2)
    data_context: Mapped[dict | None] = mapped_column(JSONB)
    confidence: Mapped[float | None] = mapped_column(Float)
    model_used: Mapped[str | None] = mapped_column(String(50))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_helpful: Mapped[bool | None] = mapped_column(Boolean)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

