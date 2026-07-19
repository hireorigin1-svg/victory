from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.character import Character
from app.models.user import User, UserRole
from app.repositories.characters import CharacterRepository
from app.schemas.character import CharacterCreate, CharacterRead, CharacterUpdate
from app.services.versioning import append_version_history

router = APIRouter(prefix="/characters", tags=["characters"])
write_roles = (UserRole.admin, UserRole.director, UserRole.editor)


@router.get("", response_model=list[CharacterRead])
def list_characters(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return CharacterRepository(db).list(limit=limit, offset=offset)


@router.post("", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
def create_character(
    payload: CharacterCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    return CharacterRepository(db).create(payload.model_dump())


@router.get("/{character_id}", response_model=CharacterRead)
def get_character(
    character_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    character = CharacterRepository(db).get(character_id)
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return character


@router.patch("/{character_id}", response_model=CharacterRead)
def update_character(
    character_id: str,
    payload: CharacterUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*write_roles)),
):
    repo = CharacterRepository(db)
    character = repo.get(character_id)
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    changes = payload.model_dump(exclude_unset=True)
    before = _snapshot(character)
    changes["version_history"] = append_version_history(
        character.version_history, before, actor.id
    )
    return repo.update(character, changes)


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(
    character_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    repo = CharacterRepository(db)
    character = repo.get(character_id)
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    repo.delete(character)


def _snapshot(character: Character) -> dict:
    return {
        key: getattr(character, key)
        for key in CharacterCreate.model_fields.keys()
    }
