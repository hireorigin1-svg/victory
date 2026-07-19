from app.models.environment import Environment
from app.repositories.base import SQLAlchemyRepository


class EnvironmentRepository(SQLAlchemyRepository[Environment]):
    model = Environment
