from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class LLMInteraction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "llm_interactions"

    workflow_id: Mapped[str | None] = mapped_column(ForeignKey("director_workflows.id"), index=True)
    shot_id: Mapped[str | None] = mapped_column(ForeignKey("shots.id"), index=True)
    provider: Mapped[str] = mapped_column(String(80), index=True)
    model: Mapped[str | None] = mapped_column(String(160))
    purpose: Mapped[str] = mapped_column(String(120), index=True)
    request_context: Mapped[dict] = mapped_column(JSON, default=dict)
    instruction: Mapped[str] = mapped_column(Text)
    response_text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(80), default="success")
    error_message: Mapped[str | None] = mapped_column(Text)
