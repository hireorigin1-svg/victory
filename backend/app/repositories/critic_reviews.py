from sqlalchemy import select

from app.models.critic_review import CriticReview
from app.repositories.base import SQLAlchemyRepository


class CriticReviewRepository(SQLAlchemyRepository[CriticReview]):
    model = CriticReview

    def list_for_shot(self, shot_id: str) -> list[CriticReview]:
        return list(self.db.scalars(select(CriticReview).where(CriticReview.shot_id == shot_id)).all())
