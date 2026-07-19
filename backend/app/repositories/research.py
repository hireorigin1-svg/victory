from sqlalchemy import select

from app.models.research import (
    ABTestGroup,
    CharacterIdentityProfile,
    ProductionMetric,
    PromptGenome,
    ProviderBehaviorRecord,
    SceneSimulation,
)
from app.repositories.base import SQLAlchemyRepository


class PromptGenomeRepository(SQLAlchemyRepository[PromptGenome]):
    model = PromptGenome

    def list_for_shot(self, shot_id: str) -> list[PromptGenome]:
        return list(self.db.scalars(select(PromptGenome).where(PromptGenome.shot_id == shot_id)).all())


class ProviderBehaviorRepository(SQLAlchemyRepository[ProviderBehaviorRecord]):
    model = ProviderBehaviorRecord

    def list_for_provider(self, provider: str) -> list[ProviderBehaviorRecord]:
        return list(
            self.db.scalars(
                select(ProviderBehaviorRecord).where(ProviderBehaviorRecord.provider == provider)
            ).all()
        )


class ABTestGroupRepository(SQLAlchemyRepository[ABTestGroup]):
    model = ABTestGroup


class CharacterIdentityProfileRepository(SQLAlchemyRepository[CharacterIdentityProfile]):
    model = CharacterIdentityProfile

    def get_for_character(self, character_id: str) -> CharacterIdentityProfile | None:
        return self.db.scalars(
            select(CharacterIdentityProfile).where(CharacterIdentityProfile.character_id == character_id)
        ).first()


class SceneSimulationRepository(SQLAlchemyRepository[SceneSimulation]):
    model = SceneSimulation

    def latest_for_scene(self, scene_id: str) -> SceneSimulation | None:
        return self.db.scalars(
            select(SceneSimulation)
            .where(SceneSimulation.scene_id == scene_id)
            .order_by(SceneSimulation.created_at.desc())
        ).first()


class ProductionMetricRepository(SQLAlchemyRepository[ProductionMetric]):
    model = ProductionMetric
