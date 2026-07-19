from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class FilmBible(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "film_bibles"

    project_name: Mapped[str] = mapped_column(String(255), default="Default Project")
    characters: Mapped[list] = mapped_column(JSON, default=list)
    relationships: Mapped[list] = mapped_column(JSON, default=list)
    locations: Mapped[list] = mapped_column(JSON, default=list)
    costumes: Mapped[list] = mapped_column(JSON, default=list)
    weapons: Mapped[list] = mapped_column(JSON, default=list)
    vehicles: Mapped[list] = mapped_column(JSON, default=list)
    lighting_style: Mapped[str | None] = mapped_column(String(255))
    color_palette: Mapped[list] = mapped_column(JSON, default=list)
    camera_rules: Mapped[list] = mapped_column(JSON, default=list)
    lens_package: Mapped[list] = mapped_column(JSON, default=list)
    action_rules: Mapped[list] = mapped_column(JSON, default=list)
    weather_rules: Mapped[list] = mapped_column(JSON, default=list)
    timeline: Mapped[list] = mapped_column(JSON, default=list)
    continuity_rules: Mapped[list] = mapped_column(JSON, default=list)
    version_history: Mapped[list] = mapped_column(JSON, default=list)
