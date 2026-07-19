from datetime import datetime

from pydantic import BaseModel, Field


class SceneBase(BaseModel):
    scene_number: int = Field(ge=1)
    script: str = Field(min_length=1)
    environment_id: str | None = None
    character_ids: list[str] = Field(default_factory=list)
    prop_ids: list[str] = Field(default_factory=list)
    timeline: str | None = None
    approved_shot_ids: list[str] = Field(default_factory=list)


class SceneCreate(SceneBase):
    pass


class SceneUpdate(BaseModel):
    scene_number: int | None = Field(default=None, ge=1)
    script: str | None = None
    environment_id: str | None = None
    character_ids: list[str] | None = None
    prop_ids: list[str] | None = None
    timeline: str | None = None
    approved_shot_ids: list[str] | None = None


class SceneRead(SceneBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
