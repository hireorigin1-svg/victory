from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.director_os import DirectorOSV2RunRequest, DirectorOSV2RunResponse
from app.services.director_os_v2 import DirectorOSV2

router = APIRouter(prefix="/director-os", tags=["director-os"])


@router.post("/v2/run", response_model=DirectorOSV2RunResponse)
def run_director_os_v2(
    payload: DirectorOSV2RunRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    try:
        return DirectorOSV2(db).run(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
