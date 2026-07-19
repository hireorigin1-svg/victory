from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class DirectorWorkflow(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "director_workflows"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    director_instruction: Mapped[str] = mapped_column(Text)
    gpt_prompt: Mapped[str | None] = mapped_column(Text)
    claude_prompt: Mapped[str | None] = mapped_column(Text)
    higgsfield_prompt: Mapped[str | None] = mapped_column(Text)
    uploaded_image_url: Mapped[str | None] = mapped_column(String(1024))
    uploaded_video_url: Mapped[str | None] = mapped_column(String(1024))
    approval_status: Mapped[str] = mapped_column(String(80), default="prompt_generated")
    review_reasons: Mapped[list] = mapped_column(JSON, default=list)
    improved_gpt_prompt: Mapped[str | None] = mapped_column(Text)
    improved_claude_prompt: Mapped[str | None] = mapped_column(Text)
    llm_context: Mapped[dict] = mapped_column(JSON, default=dict)
    workflow_events: Mapped[list] = mapped_column(JSON, default=list)
