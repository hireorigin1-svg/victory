from sqlalchemy import ForeignKey, Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ShotBlueprint(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "shot_blueprints"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    provider: Mapped[str] = mapped_column(String(120), default="higgsfield")
    blueprint: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence_score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(80), default="draft")


class KnowledgePacket(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_packets"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    blueprint_id: Mapped[str] = mapped_column(ForeignKey("shot_blueprints.id"), index=True)
    retrieval_query: Mapped[dict] = mapped_column(JSON, default=dict)
    packet: Mapped[dict] = mapped_column(JSON, default=dict)


class ProviderTranslation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "provider_translations"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    blueprint_id: Mapped[str] = mapped_column(ForeignKey("shot_blueprints.id"), index=True)
    provider: Mapped[str] = mapped_column(String(120), default="higgsfield")
    provider_model: Mapped[str | None] = mapped_column(String(120))
    translated_prompt: Mapped[str] = mapped_column(Text)
    translation_notes: Mapped[list] = mapped_column(JSON, default=list)
