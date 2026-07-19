from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.scenes import SceneRepository
from app.schemas.scene import SceneCreate, SceneRead, SceneUpdate

router = APIRouter(prefix="/scenes", tags=["scenes"])
write_roles = (UserRole.admin, UserRole.director, UserRole.editor)


@router.get("", response_model=list[SceneRead])
def list_scenes(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return SceneRepository(db).list()


@router.post("", response_model=SceneRead, status_code=status.HTTP_201_CREATED)
def create_scene(
    payload: SceneCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    return SceneRepository(db).create(payload.model_dump())


@router.get("/{scene_id}", response_model=SceneRead)
def get_scene(
    scene_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    scene = SceneRepository(db).get(scene_id)
    if not scene:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return scene


@router.patch("/{scene_id}", response_model=SceneRead)
def update_scene(
    scene_id: str,
    payload: SceneUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    repo = SceneRepository(db)
    scene = repo.get(scene_id)
    if not scene:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return repo.update(scene, payload.model_dump(exclude_unset=True))


@router.delete("/{scene_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scene(
    scene_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    repo = SceneRepository(db)
    scene = repo.get(scene_id)
    if not scene:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    repo.delete(scene)
