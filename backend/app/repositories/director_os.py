from app.models.director_os import KnowledgePacket, ProviderTranslation, ShotBlueprint
from app.repositories.base import SQLAlchemyRepository


class ShotBlueprintRepository(SQLAlchemyRepository[ShotBlueprint]):
    model = ShotBlueprint


class KnowledgePacketRepository(SQLAlchemyRepository[KnowledgePacket]):
    model = KnowledgePacket


class ProviderTranslationRepository(SQLAlchemyRepository[ProviderTranslation]):
    model = ProviderTranslation
