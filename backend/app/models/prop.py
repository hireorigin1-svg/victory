from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Prop(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "props"

    name: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[str] = mapped_column(String(80), default="object")
    description: Mapped[str | None] = mapped_column(Text)
    position: Mapped[str | None] = mapped_column(String(255))
    damage_state: Mapped[str | None] = mapped_column(String(255))
    reference_images: Mapped[list] = mapped_column(JSON, default=list)
    version_history: Mapped[list] = mapped_column(JSON, default=list)
