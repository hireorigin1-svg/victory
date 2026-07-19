from sqlalchemy import select

from app.models.film_bible import FilmBible
from app.repositories.base import SQLAlchemyRepository


class FilmBibleRepository(SQLAlchemyRepository[FilmBible]):
    model = FilmBible

    def get_singleton(self) -> FilmBible | None:
        return self.db.scalars(select(FilmBible).order_by(FilmBible.created_at)).first()
