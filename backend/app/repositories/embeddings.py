from sqlalchemy import select

from app.models.embedding import CharacterEmbedding
from app.repositories.base import SQLAlchemyRepository


class CharacterEmbeddingRepository(SQLAlchemyRepository[CharacterEmbedding]):
    model = CharacterEmbedding

    def list_for_character(self, character_id: str) -> list[CharacterEmbedding]:
        return list(
            self.db.scalars(
                select(CharacterEmbedding).where(CharacterEmbedding.character_id == character_id)
            ).all()
        )
