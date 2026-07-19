from datetime import datetime

from pydantic import BaseModel, Field


class VisualMemoryRead(BaseModel):
    id: str
    shot_id: str
    scene_id: str
    character_id: str | None = None
    approved_image: str | None = None
    state: dict = Field(default_factory=dict)
    extraction_source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MovieStateRead(BaseModel):
    id: str
    project_name: str
    current_scene_id: str | None = None
    current_shot_id: str | None = None
    state: dict = Field(default_factory=dict)
    history: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CharacterEmbeddingRead(BaseModel):
    id: str
    character_id: str
    source_shot_id: str | None = None
    source_image: str | None = None
    vector: list[float] = Field(default_factory=list)
    metadata_json: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
