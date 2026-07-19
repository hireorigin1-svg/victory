from app.models.prop import Prop
from app.repositories.base import SQLAlchemyRepository


class PropRepository(SQLAlchemyRepository[Prop]):
    model = Prop
