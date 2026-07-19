from sqlalchemy import select

from app.models.llm_interaction import LLMInteraction
from app.repositories.base import SQLAlchemyRepository


class LLMInteractionRepository(SQLAlchemyRepository[LLMInteraction]):
    model = LLMInteraction

    def list_for_workflow(self, workflow_id: str) -> list[LLMInteraction]:
        return list(
            self.db.scalars(
                select(LLMInteraction)
                .where(LLMInteraction.workflow_id == workflow_id)
                .order_by(LLMInteraction.created_at)
            ).all()
        )
