from sqlalchemy import select

from app.models.generation_experiment import GenerationExperiment
from app.repositories.base import SQLAlchemyRepository


class GenerationExperimentRepository(SQLAlchemyRepository[GenerationExperiment]):
    model = GenerationExperiment

    def list_for_shot(self, shot_id: str) -> list[GenerationExperiment]:
        return list(
            self.db.scalars(
                select(GenerationExperiment)
                .where(GenerationExperiment.shot_id == shot_id)
                .order_by(GenerationExperiment.created_at)
            ).all()
        )
