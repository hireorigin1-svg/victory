from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class SQLAlchemyRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, item_id: str) -> ModelT | None:
        return self.db.get(self.model, item_id)

    def list(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        statement = select(self.model).offset(offset).limit(limit)
        return list(self.db.scalars(statement).all())

    def create(self, payload: dict) -> ModelT:
        item = self.model(**payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item: ModelT, payload: dict) -> ModelT:
        for key, value in payload.items():
            setattr(item, key, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: ModelT) -> None:
        self.db.delete(item)
        self.db.commit()
