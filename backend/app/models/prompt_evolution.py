from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PromptEvolution(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "prompt_evolutions"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    experiment_id: Mapped[str | None] = mapped_column(ForeignKey("generation_experiments.id"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    prompt: Mapped[str] = mapped_column(Text)
    critic_summary: Mapped[str | None] = mapped_column(Text)
    continuity_score: Mapped[float | None] = mapped_column(Float)
