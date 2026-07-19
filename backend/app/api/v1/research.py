from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.characters import CharacterRepository
from app.repositories.critic_reviews import CriticReviewRepository
from app.repositories.embeddings import CharacterEmbeddingRepository
from app.repositories.generation_experiments import GenerationExperimentRepository
from app.repositories.research import (
    ABTestGroupRepository,
    CharacterIdentityProfileRepository,
    PromptGenomeRepository,
    ProviderBehaviorRepository,
    SceneSimulationRepository,
)
from app.repositories.shots import ShotRepository
from app.schemas.research import (
    ABTestRead,
    ABTestRequest,
    CharacterIdentityProfileRead,
    ProductionAnalyticsRead,
    PromptGenomeRead,
    ProviderBehaviorRead,
    SceneSimulationRead,
)
from app.services.ab_testing import ABTestingService
from app.services.identity_profile import CharacterIdentityModel
from app.services.production_analytics import ProductionAnalytics
from app.services.prompt_scientist import PromptScientist
from app.services.provider_behavior import ProviderBehaviorMiner
from app.services.scene_simulator import SceneSimulator

router = APIRouter(prefix="/research", tags=["ai-research-layer"])


@router.get("/shots/{shot_id}/genomes", response_model=list[PromptGenomeRead])
def list_prompt_genomes(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return PromptGenomeRepository(db).list_for_shot(shot_id)


@router.get("/provider-behavior", response_model=list[ProviderBehaviorRead])
def list_provider_behavior(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ProviderBehaviorRepository(db).list(limit=1000)


@router.get("/provider-behavior/summary")
def provider_behavior_summary(
    provider: str = "higgsfield",
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ProviderBehaviorMiner(ProviderBehaviorRepository(db)).summarize(provider)


@router.post("/ab-tests", response_model=ABTestRead)
def run_ab_test(
    payload: ABTestRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    shot = ShotRepository(db).get(payload.shot_id)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shot not found")
    return ABTestingService(db, ABTestGroupRepository(db)).run(
        shot=shot,
        provider=payload.provider,
        variants=payload.variants,
    )


@router.post("/characters/{character_id}/identity-profile", response_model=CharacterIdentityProfileRead)
def rebuild_identity_profile(
    character_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    character = CharacterRepository(db).get(character_id)
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return CharacterIdentityModel(
        CharacterIdentityProfileRepository(db),
        CharacterEmbeddingRepository(db),
    ).rebuild(character)


@router.post("/scenes/{scene_id}/simulate", response_model=SceneSimulationRead)
def simulate_scene(
    scene_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director, UserRole.editor)),
):
    try:
        return SceneSimulator(db, SceneSimulationRepository(db)).simulate(scene_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/analytics", response_model=ProductionAnalyticsRead)
def production_analytics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ProductionAnalytics(ShotRepository(db), GenerationExperimentRepository(db)).dashboard()


@router.get("/shots/{shot_id}/scientist-diagnosis")
def scientist_diagnosis(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    genomes = PromptGenomeRepository(db).list_for_shot(shot_id)
    reviews = CriticReviewRepository(db).list_for_shot(shot_id)
    if not genomes or not reviews:
        return {"drift_fields": [], "suspect_genes": {}, "rewrites": []}
    return PromptScientist().diagnose(genomes[-1], reviews[-1])
