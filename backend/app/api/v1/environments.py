from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.environment import Environment
from app.models.user import User, UserRole
from app.repositories.environments import EnvironmentRepository
from app.schemas.environment import EnvironmentCreate, EnvironmentRead, EnvironmentUpdate
from app.services.versioning import append_version_history

router = APIRouter(prefix="/environments", tags=["environments"])
write_roles = (UserRole.admin, UserRole.director, UserRole.editor)


@router.get("", response_model=list[EnvironmentRead])
def list_environments(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return EnvironmentRepository(db).list(limit=limit, offset=offset)


@router.post("", response_model=EnvironmentRead, status_code=status.HTTP_201_CREATED)
def create_environment(
    payload: EnvironmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    return EnvironmentRepository(db).create(payload.model_dump())


@router.get("/{environment_id}", response_model=EnvironmentRead)
def get_environment(
    environment_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    environment = EnvironmentRepository(db).get(environment_id)
    if not environment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return environment


@router.patch("/{environment_id}", response_model=EnvironmentRead)
def update_environment(
    environment_id: str,
    payload: EnvironmentUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*write_roles)),
):
    repo = EnvironmentRepository(db)
    environment = repo.get(environment_id)
    if not environment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    changes = payload.model_dump(exclude_unset=True)
    before = _snapshot(environment)
    changes["version_history"] = append_version_history(
        environment.version_history, before, actor.id
    )
    return repo.update(environment, changes)


@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environment(
    environment_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    repo = EnvironmentRepository(db)
    environment = repo.get(environment_id)
    if not environment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    repo.delete(environment)


def _snapshot(environment: Environment) -> dict:
    return {
        key: getattr(environment, key)
        for key in EnvironmentCreate.model_fields.keys()
    }
