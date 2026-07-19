from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.cameras import CameraRepository
from app.schemas.camera import CameraCreate, CameraRead, CameraUpdate

router = APIRouter(prefix="/cameras", tags=["cameras"])
write_roles = (UserRole.admin, UserRole.director, UserRole.editor)


@router.get("", response_model=list[CameraRead])
def list_cameras(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return CameraRepository(db).list()


@router.post("", response_model=CameraRead, status_code=status.HTTP_201_CREATED)
def create_camera(
    payload: CameraCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    return CameraRepository(db).create(payload.model_dump())


@router.get("/{camera_id}", response_model=CameraRead)
def get_camera(
    camera_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    camera = CameraRepository(db).get(camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return camera


@router.patch("/{camera_id}", response_model=CameraRead)
def update_camera(
    camera_id: str,
    payload: CameraUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    repo = CameraRepository(db)
    camera = repo.get(camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return repo.update(camera, payload.model_dump(exclude_unset=True))


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(
    camera_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    repo = CameraRepository(db)
    camera = repo.get(camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    repo.delete(camera)
