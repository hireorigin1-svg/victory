from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class CharacterEmbedding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "character_embeddings"

    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), index=True)
    source_shot_id: Mapped[str | None] = mapped_column(ForeignKey("shots.id"))
    source_image: Mapped[str | None] = mapped_column(String(1024))
    vector: Mapped[list] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
