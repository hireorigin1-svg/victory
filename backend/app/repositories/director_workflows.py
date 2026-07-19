from sqlalchemy import select

from app.models.director_workflow import DirectorWorkflow
from app.repositories.base import SQLAlchemyRepository


class DirectorWorkflowRepository(SQLAlchemyRepository[DirectorWorkflow]):
    model = DirectorWorkflow

    def list_latest(self, limit: int = 50) -> list[DirectorWorkflow]:
        return list(
            self.db.scalars(
                select(DirectorWorkflow)
                .order_by(DirectorWorkflow.updated_at.desc())
                .limit(limit)
            ).all()
        )
