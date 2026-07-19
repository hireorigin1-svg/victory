from sqlalchemy import select

from app.models.shot import Shot, ShotStatus
from app.repositories.base import SQLAlchemyRepository


class ShotRepository(SQLAlchemyRepository[Shot]):
    model = Shot

    def list_for_scene(self, scene_id: str) -> list[Shot]:
        return list(
            self.db.scalars(
                select(Shot).where(Shot.scene_id == scene_id).order_by(Shot.shot_number)
            ).all()
        )

    def get_previous_approved(self, scene_id: str, shot_number: int) -> Shot | None:
        return self.db.scalars(
            select(Shot)
            .where(
                Shot.scene_id == scene_id,
                Shot.shot_number < shot_number,
                Shot.status == ShotStatus.approved,
            )
            .order_by(Shot.shot_number.desc())
        ).first()
