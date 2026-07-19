from datetime import datetime

from pydantic import BaseModel, Field


class CameraBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    lens: str | None = None
    camera_angle: str | None = None
    movement: str | None = None
    aspect_ratio: str | None = None
    depth_of_field: str | None = None
    fps: str | None = None
    motion_blur: str | None = None
    film_look: str | None = None


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    lens: str | None = None
    camera_angle: str | None = None
    movement: str | None = None
    aspect_ratio: str | None = None
    depth_of_field: str | None = None
    fps: str | None = None
    motion_blur: str | None = None
    film_look: str | None = None


class CameraRead(CameraBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
