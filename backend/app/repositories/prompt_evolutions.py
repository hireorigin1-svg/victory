from sqlalchemy import select

from app.models.prompt_evolution import PromptEvolution
from app.repositories.base import SQLAlchemyRepository


class PromptEvolutionRepository(SQLAlchemyRepository[PromptEvolution]):
    model = PromptEvolution

    def list_for_shot(self, shot_id: str) -> list[PromptEvolution]:
        return list(
            self.db.scalars(
                select(PromptEvolution)
                .where(PromptEvolution.shot_id == shot_id)
                .order_by(PromptEvolution.version)
            ).all()
        )
