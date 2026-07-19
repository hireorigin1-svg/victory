from sqlalchemy import select

from app.models.scene import Scene
from app.repositories.base import SQLAlchemyRepository


class SceneRepository(SQLAlchemyRepository[Scene]):
    model = Scene

    def get_by_number(self, scene_number: int) -> Scene | None:
        return self.db.scalars(
            select(Scene).where(Scene.scene_number == scene_number)
        ).first()
