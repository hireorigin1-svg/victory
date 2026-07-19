from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.shot import ContinuityReport, ShotRead


class FeedbackLoopRequest(BaseModel):
    shot_id: str
    provider: str = "mock"
    max_attempts: int = Field(default=5, ge=1, le=5)


class ExperimentRead(BaseModel):
    id: str
    shot_id: str
    prompt_hash: str
    provider: str
    provider_model: str | None = None
    face_score: float | None = None
    body_score: float | None = None
    costume_score: float | None = None
    environment_score: float | None = None
    lighting_score: float | None = None
    camera_score: float | None = None
    overall_score: float | None = None
    accepted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CriticReviewRead(BaseModel):
    id: str
    shot_id: str
    experiment_id: str | None = None
    critic_role: str
    differences: list = Field(default_factory=list)
    suggested_corrections: list = Field(default_factory=list)
    corrected_prompt: str | None = None
    overall_score: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromptEvolutionRead(BaseModel):
    id: str
    shot_id: str
    experiment_id: str | None = None
    version: int
    prompt: str
    critic_summary: str | None = None
    continuity_score: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ShotDNARead(BaseModel):
    id: str
    shot_id: str
    scene_id: str
    character_id: str | None = None
    source_image: str | None = None
    dna: dict = Field(default_factory=dict)
    extractor: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MemoryGraphNodeRead(BaseModel):
    id: str
    label: str
    entity_type: str
    entity_id: str | None = None
    properties: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class MemoryGraphEdgeRead(BaseModel):
    id: str
    source_node_id: str
    relation: str
    target_node_id: str
    introduced_scene_id: str | None = None
    introduced_shot_id: str | None = None
    properties: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class FeedbackLoopResponse(BaseModel):
    shot: ShotRead
    experiment: ExperimentRead | None
    critic_review: CriticReviewRead | None
    quality_report: ContinuityReport | None
    accepted: bool
    versions: int
