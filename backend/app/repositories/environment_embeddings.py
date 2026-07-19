from sqlalchemy import select

from app.models.environment_embedding import EnvironmentEmbedding
from app.repositories.base import SQLAlchemyRepository


class EnvironmentEmbeddingRepository(SQLAlchemyRepository[EnvironmentEmbedding]):
    model = EnvironmentEmbedding

    def list_for_environment(self, environment_id: str) -> list[EnvironmentEmbedding]:
        return list(
            self.db.scalars(
                select(EnvironmentEmbedding).where(EnvironmentEmbedding.environment_id == environment_id)
            ).all()
        )
