from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.critic_reviews import CriticReviewRepository
from app.repositories.generation_experiments import GenerationExperimentRepository
from app.repositories.memory_graph import MemoryGraphEdgeRepository, MemoryGraphNodeRepository
from app.repositories.prompt_evolutions import PromptEvolutionRepository
from app.repositories.shot_dna import ShotDNARepository
from app.repositories.shots import ShotRepository
from app.schemas.brain import (
    CriticReviewRead,
    ExperimentRead,
    FeedbackLoopRequest,
    FeedbackLoopResponse,
    MemoryGraphEdgeRead,
    MemoryGraphNodeRead,
    PromptEvolutionRead,
    ShotDNARead,
)
from app.services.director_feedback_loop import DirectorFeedbackLoop
from app.services.director_memory import DirectorMemory

router = APIRouter(prefix="/brain", tags=["ai-director-brain"])


@router.post("/feedback-loop", response_model=FeedbackLoopResponse)
def run_feedback_loop(
    payload: FeedbackLoopRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    shot = ShotRepository(db).get(payload.shot_id)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shot not found")
    return DirectorFeedbackLoop(db).run(
        shot=shot,
        provider_name=payload.provider,
        max_attempts=payload.max_attempts,
    )


@router.get("/experiments", response_model=list[ExperimentRead])
def list_experiments(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return GenerationExperimentRepository(db).list(limit=1000)


@router.get("/experiments/summary")
def experiment_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return DirectorMemory(GenerationExperimentRepository(db)).summarize()


@router.get("/shots/{shot_id}/critic-reviews", response_model=list[CriticReviewRead])
def list_critic_reviews(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return CriticReviewRepository(db).list_for_shot(shot_id)


@router.get("/shots/{shot_id}/prompt-evolution", response_model=list[PromptEvolutionRead])
def list_prompt_evolution(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return PromptEvolutionRepository(db).list_for_shot(shot_id)


@router.get("/shots/{shot_id}/dna", response_model=ShotDNARead | None)
def get_shot_dna(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ShotDNARepository(db).get_for_shot(shot_id)


@router.get("/memory-graph/nodes", response_model=list[MemoryGraphNodeRead])
def list_graph_nodes(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return MemoryGraphNodeRepository(db).list(limit=1000)


@router.get("/memory-graph/edges", response_model=list[MemoryGraphEdgeRead])
def list_graph_edges(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return MemoryGraphEdgeRepository(db).list_edges()
