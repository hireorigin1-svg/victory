from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class MovieState(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "movie_states"

    project_name: Mapped[str] = mapped_column(String(255), default="Default Project", unique=True)
    current_scene_id: Mapped[str | None] = mapped_column(String(36))
    current_shot_id: Mapped[str | None] = mapped_column(String(36))
    state: Mapped[dict] = mapped_column(JSON, default=dict)
    history: Mapped[list] = mapped_column(JSON, default=list)
