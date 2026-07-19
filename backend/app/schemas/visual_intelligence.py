from datetime import datetime

from pydantic import BaseModel, Field


class VisualSceneGraphRead(BaseModel):
    id: str
    shot_id: str
    source_image: str | None = None
    entities: list = Field(default_factory=list)
    relations: list = Field(default_factory=list)
    attributes: dict = Field(default_factory=dict)
    extractor: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromptASTRead(BaseModel):
    id: str
    shot_id: str
    prompt_hash: str
    ast: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VisualPlanRead(BaseModel):
    id: str
    shot_id: str
    character_blocking: list = Field(default_factory=list)
    camera: dict = Field(default_factory=dict)
    lighting: dict = Field(default_factory=dict)
    composition: dict = Field(default_factory=dict)
    color_palette: list = Field(default_factory=list)
    motion: dict = Field(default_factory=dict)
    constraints: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReferenceAssetCreate(BaseModel):
    shot_id: str | None = None
    character_id: str | None = None
    environment_id: str | None = None
    image_url: str
    approved: bool = True
    quality_score: float | None = None


class ReferenceAssetRead(ReferenceAssetCreate):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReferenceSegmentRead(BaseModel):
    id: str
    reference_asset_id: str
    segment_type: str
    crop_url: str | None = None
    embedding: list[float] = Field(default_factory=list)
    features: dict = Field(default_factory=dict)
    quality_score: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReferenceSelectionRequest(BaseModel):
    shot_id: str
    requested_continuity: dict = Field(default_factory=dict)


class ReferenceSelectionRead(BaseModel):
    id: str
    shot_id: str
    requested_continuity: dict = Field(default_factory=dict)
    selected_segments: list = Field(default_factory=list)
    rationale: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VisualDiffRead(BaseModel):
    id: str
    baseline_shot_id: str
    candidate_shot_id: str
    changes: list = Field(default_factory=list)
    corrections: list = Field(default_factory=list)
    overall_delta_score: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FailureClusterRead(BaseModel):
    id: str
    cluster_type: str
    experiment_ids: list = Field(default_factory=list)
    common_causes: list = Field(default_factory=list)
    recommended_actions: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CinematographyStyleCreate(BaseModel):
    name: str
    scenario: str = "general"
    camera_rules: dict = Field(default_factory=dict)
    lighting_rules: dict = Field(default_factory=dict)
    composition_rules: dict = Field(default_factory=dict)
    notes: str | None = None


class CinematographyStyleRead(CinematographyStyleCreate):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
