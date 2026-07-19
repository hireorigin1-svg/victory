from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.film_bibles import FilmBibleRepository
from app.schemas.film_bible import FilmBibleCreate, FilmBibleRead, FilmBibleUpdate
from app.services.versioning import append_version_history

router = APIRouter(prefix="/film-bible", tags=["film-bible"])
write_roles = (UserRole.admin, UserRole.director, UserRole.editor)


@router.get("", response_model=FilmBibleRead)
def get_film_bible(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    bible = FilmBibleRepository(db).get_singleton()
    if not bible:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film Bible not created")
    return bible


@router.post("", response_model=FilmBibleRead, status_code=status.HTTP_201_CREATED)
def create_film_bible(
    payload: FilmBibleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    repo = FilmBibleRepository(db)
    if repo.get_singleton():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Film Bible already exists")
    return repo.create(payload.model_dump())


@router.patch("", response_model=FilmBibleRead)
def update_film_bible(
    payload: FilmBibleUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*write_roles)),
):
    repo = FilmBibleRepository(db)
    bible = repo.get_singleton()
    if not bible:
        bible = repo.create(FilmBibleCreate().model_dump())
    changes = payload.model_dump(exclude_unset=True)
    before = {key: getattr(bible, key) for key in FilmBibleCreate.model_fields.keys()}
    changes["version_history"] = append_version_history(bible.version_history, before, actor.id)
    return repo.update(bible, changes)
