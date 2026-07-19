from sqlalchemy import Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class CriticReview(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "critic_reviews"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    experiment_id: Mapped[str | None] = mapped_column(ForeignKey("generation_experiments.id"), index=True)
    critic_role: Mapped[str] = mapped_column(String(120), default="Hollywood continuity supervisor")
    face_drift: Mapped[str | None] = mapped_column(Text)
    hair_drift: Mapped[str | None] = mapped_column(Text)
    costume_drift: Mapped[str | None] = mapped_column(Text)
    lighting_drift: Mapped[str | None] = mapped_column(Text)
    environment_drift: Mapped[str | None] = mapped_column(Text)
    camera_drift: Mapped[str | None] = mapped_column(Text)
    differences: Mapped[list] = mapped_column(JSON, default=list)
    suggested_corrections: Mapped[list] = mapped_column(JSON, default=list)
    corrected_prompt: Mapped[str | None] = mapped_column(Text)
    overall_score: Mapped[float | None] = mapped_column(Float)
