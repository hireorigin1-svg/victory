from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Environment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "environments"

    location: Mapped[str] = mapped_column(String(255), index=True)
    architecture: Mapped[str | None] = mapped_column(Text)
    lighting: Mapped[str | None] = mapped_column(Text)
    weather: Mapped[str | None] = mapped_column(String(120))
    time: Mapped[str | None] = mapped_column(String(120))
    props: Mapped[list] = mapped_column(JSON, default=list)
    background_assets: Mapped[list] = mapped_column(JSON, default=list)
    reference_images: Mapped[list] = mapped_column(JSON, default=list)
    version_history: Mapped[list] = mapped_column(JSON, default=list)
