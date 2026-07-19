from app.models.character import Character
from app.repositories.base import SQLAlchemyRepository


class CharacterRepository(SQLAlchemyRepository[Character]):
    model = Character
