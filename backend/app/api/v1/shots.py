from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.shot import ShotStatus
from app.models.user import User, UserRole
from app.repositories.scenes import SceneRepository
from app.repositories.shots import ShotRepository
from app.schemas.shot import (
    ContinuityReport,
    PromptCompileRequest,
    PromptCompileResponse,
    ShotCreate,
    ShotRead,
    ShotUpdate,
)
from app.services.continuity import ContinuityChecker
from app.services.prompt_compiler import PromptCompiler
from app.services.vision import VisionAnalyzer

router = APIRouter(prefix="/shots", tags=["shots"])
write_roles = (UserRole.admin, UserRole.director, UserRole.editor)


@router.get("", response_model=list[ShotRead])
def list_shots(
    scene_id: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repo = ShotRepository(db)
    return repo.list_for_scene(scene_id) if scene_id else repo.list()


@router.post("", response_model=ShotRead, status_code=status.HTTP_201_CREATED)
def create_shot(
    payload: ShotCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    if not SceneRepository(db).get(payload.scene_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scene not found")
    prompt, components, explanation, warnings = PromptCompiler(db).compile(
        scene_id=payload.scene_id,
        user_instruction=payload.user_instruction,
        camera_id=payload.camera_id,
    )
    data = payload.model_dump()
    data.update(
        {
            "prompt": prompt,
            "prompt_components": components,
            "director_explanation": explanation,
            "continuity_warnings": warnings,
            "status": ShotStatus.compiled,
        }
    )
    return ShotRepository(db).create(data)


@router.get("/{shot_id}", response_model=ShotRead)
def get_shot(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    shot = ShotRepository(db).get(shot_id)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return shot


@router.patch("/{shot_id}", response_model=ShotRead)
def update_shot(
    shot_id: str,
    payload: ShotUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    repo = ShotRepository(db)
    shot = repo.get(shot_id)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return repo.update(shot, payload.model_dump(exclude_unset=True))


@router.delete("/{shot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shot(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    repo = ShotRepository(db)
    shot = repo.get(shot_id)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    repo.delete(shot)


@router.post("/{shot_id}/compile", response_model=PromptCompileResponse)
def compile_shot_prompt(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    repo = ShotRepository(db)
    shot = repo.get(shot_id)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    prompt, components, explanation, warnings = PromptCompiler(db).compile(
        scene_id=shot.scene_id,
        user_instruction=shot.user_instruction,
        shot_id=shot.id,
        camera_id=shot.camera_id,
    )
    repo.update(
        shot,
        {
            "prompt": prompt,
            "prompt_components": components,
            "director_explanation": explanation,
            "continuity_warnings": warnings,
            "status": ShotStatus.compiled,
        },
    )
    return PromptCompileResponse(prompt=prompt, components=components, explanation=explanation, warnings=warnings)


@router.post("/{shot_id}/analyze-vision", response_model=ShotRead)
def analyze_vision(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    repo = ShotRepository(db)
    shot = repo.get(shot_id)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    analysis = VisionAnalyzer().analyze(shot)
    return repo.update(shot, {"vision_analysis": analysis})


@router.post("/{shot_id}/continuity", response_model=ContinuityReport)
def check_continuity(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    repo = ShotRepository(db)
    shot = repo.get(shot_id)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    previous = repo.get(shot.previous_shot_id) if shot.previous_shot_id else repo.get_previous_approved(shot.scene_id, shot.shot_number)
    report = ContinuityChecker().compare(previous, shot)
    update = {
        "continuity_score": report.overall_continuity_score,
        "status": report.decision,
        "rejection_reason": "; ".join(report.notes) if report.decision == ShotStatus.rejected else None,
    }
    repo.update(shot, update)
    return report


@router.post("/compile", response_model=PromptCompileResponse)
def compile_prompt(
    payload: PromptCompileRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    try:
        prompt, components, explanation, warnings = PromptCompiler(db).compile(
            scene_id=payload.scene_id,
            user_instruction=payload.user_instruction,
            shot_id=payload.shot_id,
            camera_id=payload.camera_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PromptCompileResponse(prompt=prompt, components=components, explanation=explanation, warnings=warnings)
