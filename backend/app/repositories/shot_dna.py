from sqlalchemy import select

from app.models.shot_dna import ShotDNA
from app.repositories.base import SQLAlchemyRepository


class ShotDNARepository(SQLAlchemyRepository[ShotDNA]):
    model = ShotDNA

    def get_for_shot(self, shot_id: str) -> ShotDNA | None:
        return self.db.scalars(select(ShotDNA).where(ShotDNA.shot_id == shot_id)).first()
