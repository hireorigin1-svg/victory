from sqlalchemy import JSON, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Scene(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scenes"

    scene_number: Mapped[int] = mapped_column(Integer, index=True)
    script: Mapped[str] = mapped_column(Text)
    environment_id: Mapped[str | None] = mapped_column(ForeignKey("environments.id"))
    character_ids: Mapped[list] = mapped_column(JSON, default=list)
    prop_ids: Mapped[list] = mapped_column(JSON, default=list)
    timeline: Mapped[str | None] = mapped_column(Text)
    approved_shot_ids: Mapped[list] = mapped_column(JSON, default=list)
