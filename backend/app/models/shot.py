from enum import StrEnum

from sqlalchemy import Float, ForeignKey, JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ShotStatus(StrEnum):
    draft = "draft"
    compiled = "compiled"
    generated = "generated"
    approved = "approved"
    rejected = "rejected"
    queued = "queued"
    needs_director_approval = "needs_director_approval"


class Shot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "shots"

    scene_id: Mapped[str] = mapped_column(ForeignKey("scenes.id"), index=True)
    shot_number: Mapped[int] = mapped_column(Integer, index=True)
    user_instruction: Mapped[str] = mapped_column(Text)
    prompt: Mapped[str | None] = mapped_column(Text)
    generated_image: Mapped[str | None] = mapped_column(String(1024))
    generated_video: Mapped[str | None] = mapped_column(String(1024))
    approved_image: Mapped[str | None] = mapped_column(String(1024))
    approved_video: Mapped[str | None] = mapped_column(String(1024))
    lighting: Mapped[str | None] = mapped_column(Text)
    emotion: Mapped[str | None] = mapped_column(String(255))
    pose: Mapped[str | None] = mapped_column(String(255))
    camera_id: Mapped[str | None] = mapped_column(ForeignKey("camera_profiles.id"))
    environment_id: Mapped[str | None] = mapped_column(ForeignKey("environments.id"))
    previous_shot_id: Mapped[str | None] = mapped_column(ForeignKey("shots.id"))
    next_shot_id: Mapped[str | None] = mapped_column(ForeignKey("shots.id"))
    quality_score: Mapped[float | None] = mapped_column(Float)
    continuity_score: Mapped[float | None] = mapped_column(Float)
    status: Mapped[ShotStatus] = mapped_column(default=ShotStatus.draft)
    prompt_components: Mapped[dict] = mapped_column(JSON, default=dict)
    vision_analysis: Mapped[dict] = mapped_column(JSON, default=dict)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    generation_attempts: Mapped[int] = mapped_column(Integer, default=0)
    director_explanation: Mapped[list] = mapped_column(JSON, default=list)
    continuity_warnings: Mapped[list] = mapped_column(JSON, default=list)
