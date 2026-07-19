from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.props import PropRepository
from app.schemas.prop import PropCreate, PropRead, PropUpdate

router = APIRouter(prefix="/props", tags=["props"])
write_roles = (UserRole.admin, UserRole.director, UserRole.editor)


@router.get("", response_model=list[PropRead])
def list_props(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return PropRepository(db).list()


@router.post("", response_model=PropRead, status_code=status.HTTP_201_CREATED)
def create_prop(
    payload: PropCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    return PropRepository(db).create(payload.model_dump())


@router.get("/{prop_id}", response_model=PropRead)
def get_prop(
    prop_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    prop = PropRepository(db).get(prop_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return prop


@router.patch("/{prop_id}", response_model=PropRead)
def update_prop(
    prop_id: str,
    payload: PropUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    repo = PropRepository(db)
    prop = repo.get(prop_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return repo.update(prop, payload.model_dump(exclude_unset=True))


@router.delete("/{prop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prop(
    prop_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    repo = PropRepository(db)
    prop = repo.get(prop_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    repo.delete(prop)
