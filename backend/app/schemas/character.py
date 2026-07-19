from datetime import datetime

from pydantic import BaseModel, Field


class CharacterBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    face: str | None = None
    hair: str | None = None
    skin: str | None = None
    height: str | None = None
    body: str | None = None
    clothes: str | None = None
    accessories: str | None = None
    voice: str | None = None
    walking_style: str | None = None
    expressions: dict = Field(default_factory=dict)
    reference_images: list[str] = Field(default_factory=list)


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    face: str | None = None
    hair: str | None = None
    skin: str | None = None
    height: str | None = None
    body: str | None = None
    clothes: str | None = None
    accessories: str | None = None
    voice: str | None = None
    walking_style: str | None = None
    expressions: dict | None = None
    reference_images: list[str] | None = None


class CharacterRead(CharacterBase):
    id: str
    version_history: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
