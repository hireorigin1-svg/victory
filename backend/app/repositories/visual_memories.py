from sqlalchemy import select

from app.models.visual_memory import VisualMemory
from app.repositories.base import SQLAlchemyRepository


class VisualMemoryRepository(SQLAlchemyRepository[VisualMemory]):
    model = VisualMemory

    def get_for_shot(self, shot_id: str) -> VisualMemory | None:
        return self.db.scalars(select(VisualMemory).where(VisualMemory.shot_id == shot_id)).first()

    def latest_for_scene(self, scene_id: str) -> VisualMemory | None:
        return self.db.scalars(
            select(VisualMemory)
            .where(VisualMemory.scene_id == scene_id)
            .order_by(VisualMemory.created_at.desc())
        ).first()
