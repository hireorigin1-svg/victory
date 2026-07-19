from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.generation_experiments import GenerationExperimentRepository
from app.repositories.shots import ShotRepository
from app.repositories.visual_intelligence import (
    CinematographyStyleRepository,
    FailureClusterRepository,
    PromptASTRepository,
    ReferenceAssetRepository,
    VisualDiffRepository,
    VisualPlanRepository,
    VisualSceneGraphRepository,
)
from app.schemas.visual_intelligence import (
    CinematographyStyleCreate,
    CinematographyStyleRead,
    FailureClusterRead,
    PromptASTRead,
    ReferenceAssetCreate,
    ReferenceAssetRead,
    ReferenceSelectionRead,
    ReferenceSelectionRequest,
    VisualDiffRead,
    VisualPlanRead,
    VisualSceneGraphRead,
)
from app.services.cinematography import CinematographyEngine
from app.services.failure_clustering import FailureClusteringService
from app.services.prompt_ast import PromptASTCompiler
from app.services.reference_intelligence import ReferenceIntelligence
from app.services.visual_compiler import VisualCompiler
from app.services.visual_diff import VisualDiffEngine
from app.services.visual_scene_graph import VisualSceneGraphExtractor

router = APIRouter(prefix="/visual-intelligence", tags=["visual-intelligence"])
write_roles = (UserRole.admin, UserRole.director, UserRole.editor)


@router.post("/references", response_model=ReferenceAssetRead, status_code=status.HTTP_201_CREATED)
def ingest_reference(
    payload: ReferenceAssetCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    asset, _ = ReferenceIntelligence(db).ingest(payload.model_dump())
    return asset


@router.get("/references", response_model=list[ReferenceAssetRead])
def list_references(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return ReferenceAssetRepository(db).list(limit=1000)


@router.post("/references/select", response_model=ReferenceSelectionRead)
def select_references(
    payload: ReferenceSelectionRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    if not ShotRepository(db).get(payload.shot_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shot not found")
    return ReferenceIntelligence(db).select_for_shot(payload.shot_id, payload.requested_continuity)


@router.post("/shots/{shot_id}/scene-graph", response_model=VisualSceneGraphRead)
def extract_scene_graph(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    shot = ShotRepository(db).get(shot_id)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shot not found")
    return VisualSceneGraphExtractor(VisualSceneGraphRepository(db)).extract(shot)


@router.post("/shots/{shot_id}/prompt-ast", response_model=PromptASTRead)
def compile_prompt_ast(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    shot = ShotRepository(db).get(shot_id)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shot not found")
    return PromptASTCompiler(PromptASTRepository(db)).compile(shot.id, shot.prompt or shot.user_instruction)


@router.post("/shots/{shot_id}/visual-plan", response_model=VisualPlanRead)
def compile_visual_plan(
    shot_id: str,
    style_name: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    try:
        return VisualCompiler(db).compile_plan(shot_id, style_name=style_name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/diff", response_model=VisualDiffRead)
def create_visual_diff(
    baseline_shot_id: str,
    candidate_shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    repo = ShotRepository(db)
    baseline = repo.get(baseline_shot_id)
    candidate = repo.get(candidate_shot_id)
    if not baseline or not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shot not found")
    return VisualDiffEngine(VisualDiffRepository(db)).compare(baseline, candidate)


@router.post("/failures/cluster", response_model=list[FailureClusterRead])
def cluster_failures(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    return FailureClusteringService(
        GenerationExperimentRepository(db),
        FailureClusterRepository(db),
    ).cluster()


@router.post("/cinematography/seed", response_model=list[CinematographyStyleRead])
def seed_cinematography_styles(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    return CinematographyEngine(CinematographyStyleRepository(db)).seed_defaults()


@router.post("/cinematography", response_model=CinematographyStyleRead)
def create_cinematography_style(
    payload: CinematographyStyleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    return CinematographyStyleRepository(db).create(payload.model_dump())


@router.get("/cinematography", response_model=list[CinematographyStyleRead])
def list_cinematography_styles(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return CinematographyStyleRepository(db).list(limit=1000)
