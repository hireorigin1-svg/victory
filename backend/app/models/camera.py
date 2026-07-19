from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class CameraProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "camera_profiles"

    name: Mapped[str] = mapped_column(String(255), index=True)
    lens: Mapped[str | None] = mapped_column(String(120))
    camera_angle: Mapped[str | None] = mapped_column(String(160))
    movement: Mapped[str | None] = mapped_column(String(160))
    aspect_ratio: Mapped[str | None] = mapped_column(String(60))
    depth_of_field: Mapped[str | None] = mapped_column(String(120))
    fps: Mapped[str | None] = mapped_column(String(60))
    motion_blur: Mapped[str | None] = mapped_column(String(120))
    film_look: Mapped[str | None] = mapped_column(Text)
