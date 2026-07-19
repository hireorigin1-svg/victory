from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ShotDNA(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "shot_dna"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), unique=True, index=True)
    scene_id: Mapped[str] = mapped_column(ForeignKey("scenes.id"), index=True)
    character_id: Mapped[str | None] = mapped_column(ForeignKey("characters.id"), index=True)
    source_image: Mapped[str | None] = mapped_column(String(1024))
    dna: Mapped[dict] = mapped_column(JSON, default=dict)
    extractor: Mapped[str] = mapped_column(String(80), default="gpt-vision-ready")
