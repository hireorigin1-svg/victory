from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Character(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "characters"

    name: Mapped[str] = mapped_column(String(255), index=True)
    face: Mapped[str | None] = mapped_column(Text)
    hair: Mapped[str | None] = mapped_column(Text)
    skin: Mapped[str | None] = mapped_column(Text)
    height: Mapped[str | None] = mapped_column(String(100))
    body: Mapped[str | None] = mapped_column(Text)
    clothes: Mapped[str | None] = mapped_column(Text)
    accessories: Mapped[str | None] = mapped_column(Text)
    voice: Mapped[str | None] = mapped_column(Text)
    walking_style: Mapped[str | None] = mapped_column(Text)
    expressions: Mapped[dict] = mapped_column(JSON, default=dict)
    reference_images: Mapped[list] = mapped_column(JSON, default=list)
    version_history: Mapped[list] = mapped_column(JSON, default=list)
