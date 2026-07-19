from datetime import datetime

from pydantic import BaseModel, Field


class EnvironmentBase(BaseModel):
    location: str = Field(min_length=1, max_length=255)
    architecture: str | None = None
    lighting: str | None = None
    weather: str | None = None
    time: str | None = None
    props: list[str] = Field(default_factory=list)
    background_assets: list[str] = Field(default_factory=list)
    reference_images: list[str] = Field(default_factory=list)


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentUpdate(BaseModel):
    location: str | None = Field(default=None, min_length=1, max_length=255)
    architecture: str | None = None
    lighting: str | None = None
    weather: str | None = None
    time: str | None = None
    props: list[str] | None = None
    background_assets: list[str] | None = None
    reference_images: list[str] | None = None


class EnvironmentRead(EnvironmentBase):
    id: str
    version_history: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
