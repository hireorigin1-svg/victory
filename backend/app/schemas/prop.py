from datetime import datetime

from pydantic import BaseModel, Field


class PropBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = "object"
    description: str | None = None
    position: str | None = None
    damage_state: str | None = None
    reference_images: list[str] = Field(default_factory=list)


class PropCreate(PropBase):
    pass


class PropUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = None
    description: str | None = None
    position: str | None = None
    damage_state: str | None = None
    reference_images: list[str] | None = None


class PropRead(PropBase):
    id: str
    version_history: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
