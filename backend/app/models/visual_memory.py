from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class VisualMemory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "visual_memories"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), unique=True, index=True)
    scene_id: Mapped[str] = mapped_column(ForeignKey("scenes.id"), index=True)
    character_id: Mapped[str | None] = mapped_column(ForeignKey("characters.id"), index=True)
    approved_image: Mapped[str | None] = mapped_column(String(1024))
    state: Mapped[dict] = mapped_column(JSON, default=dict)
    extraction_source: Mapped[str] = mapped_column(String(80), default="deterministic")
