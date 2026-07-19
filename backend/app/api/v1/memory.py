from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.embeddings import CharacterEmbeddingRepository
from app.repositories.movie_states import MovieStateRepository
from app.repositories.visual_memories import VisualMemoryRepository
from app.schemas.memory import CharacterEmbeddingRead, MovieStateRead, VisualMemoryRead

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/visual", response_model=list[VisualMemoryRead])
def list_visual_memory(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return VisualMemoryRepository(db).list()


@router.get("/movie-state", response_model=MovieStateRead | None)
def get_movie_state(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return MovieStateRepository(db).get_default()


@router.get("/embeddings/{character_id}", response_model=list[CharacterEmbeddingRead])
def list_character_embeddings(
    character_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return CharacterEmbeddingRepository(db).list_for_character(character_id)
