from sqlalchemy import Boolean, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class GenerationExperiment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "generation_experiments"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    prompt_hash: Mapped[str] = mapped_column(String(64), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(120), default="mock")
    provider_model: Mapped[str | None] = mapped_column(String(120))
    reference: Mapped[str | None] = mapped_column(String(255))
    generated_image: Mapped[str | None] = mapped_column(String(1024))
    generated_video: Mapped[str | None] = mapped_column(String(1024))
    face_score: Mapped[float | None] = mapped_column(Float)
    body_score: Mapped[float | None] = mapped_column(Float)
    costume_score: Mapped[float | None] = mapped_column(Float)
    environment_score: Mapped[float | None] = mapped_column(Float)
    lighting_score: Mapped[float | None] = mapped_column(Float)
    camera_score: Mapped[float | None] = mapped_column(Float)
    overall_score: Mapped[float | None] = mapped_column(Float)
    accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
