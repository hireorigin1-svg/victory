from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.shot import ShotStatus
from app.models.user import User, UserRole
from app.repositories.shots import ShotRepository
from app.schemas.director import DirectorRunRequest, DirectorRunResponse
from app.schemas.shot import ShotRead
from app.services.director_engine import DirectorEngine

router = APIRouter(prefix="/director", tags=["director"])


@router.post("/run", response_model=DirectorRunResponse)
def run_director(
    payload: DirectorRunRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    result = DirectorEngine(db).run(
        script=payload.script,
        user_instruction=payload.user_instruction,
        max_attempts=payload.max_attempts,
    )
    return result


@router.post("/shots/{shot_id}/approve", response_model=ShotRead)
def approve_shot(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    try:
        result = DirectorEngine(db).approve_shot(shot_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result["shot"]


@router.post("/shots/{shot_id}/queue-generation", response_model=ShotRead)
def queue_generation(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    repo = ShotRepository(db)
    shot = repo.get(shot_id)
    if not shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return repo.update(shot, {"status": ShotStatus.queued})
