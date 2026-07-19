from datetime import datetime

from pydantic import BaseModel, Field


class PromptGenomeRead(BaseModel):
    id: str
    shot_id: str
    experiment_id: str | None = None
    prompt_hash: str
    genes: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProviderBehaviorRead(BaseModel):
    id: str
    provider: str
    provider_model: str | None = None
    provider_version: str | None = None
    reference_strength: float | None = None
    face_score: float | None = None
    camera_score: float | None = None
    lighting_score: float | None = None
    environment_score: float | None = None
    costume_score: float | None = None
    learned_observations: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ABTestRequest(BaseModel):
    shot_id: str
    provider: str = "mock"
    variants: list[dict] | None = None


class ABTestRead(BaseModel):
    id: str
    shot_id: str
    provider: str
    variants: list = Field(default_factory=list)
    winning_experiment_id: str | None = None
    winning_variant: str | None = None
    winner_score: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CharacterIdentityProfileRead(BaseModel):
    id: str
    character_id: str
    approved_image_count: int
    canonical_vector: list[float] = Field(default_factory=list)
    profile: dict = Field(default_factory=dict)
    stability_score: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SceneSimulationRead(BaseModel):
    id: str
    scene_id: str
    expected_state: dict = Field(default_factory=dict)
    detected_conflicts: list = Field(default_factory=list)
    recommended_prompt_constraints: list = Field(default_factory=list)
    safe_to_generate: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductionAnalyticsRead(BaseModel):
    average_generations_to_approval: float
    success_rate_by_provider: dict[str, float]
    average_score_by_provider: dict[str, float]
    continuity_failures_by_category: dict[str, int]
    best_prompt_genes: dict[str, list[str]]
    cost_per_accepted_shot: float
