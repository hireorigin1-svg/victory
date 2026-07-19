from sqlalchemy import select

from app.models.movie_state import MovieState
from app.repositories.base import SQLAlchemyRepository


class MovieStateRepository(SQLAlchemyRepository[MovieState]):
    model = MovieState

    def get_default(self) -> MovieState | None:
        return self.db.scalars(select(MovieState).order_by(MovieState.created_at)).first()
