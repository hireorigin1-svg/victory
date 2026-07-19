from app.models.camera import CameraProfile
from app.repositories.base import SQLAlchemyRepository


class CameraRepository(SQLAlchemyRepository[CameraProfile]):
    model = CameraProfile
