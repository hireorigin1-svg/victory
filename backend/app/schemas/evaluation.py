from datetime import datetime

from pydantic import BaseModel, Field


class BenchmarkProjectRead(BaseModel):
    id: str
    name: str
    description: str | None = None
    character_count: int
    environment_count: int
    shot_count: int
    scenario: str
    spec: dict = Field(default_factory=dict)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BenchmarkRunRequest(BaseModel):
    benchmark_id: str
    provider: str = "mock"
    model_version: str | None = None
    pipeline_version: str = "local"


class BenchmarkRunRead(BaseModel):
    id: str
    benchmark_id: str
    provider: str
    model_version: str | None = None
    pipeline_version: str
    status: str
    summary_scores: dict = Field(default_factory=dict)
    total_cost: float
    total_latency_ms: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BenchmarkShotScoreRead(BaseModel):
    id: str
    benchmark_run_id: str
    shot_id: str | None = None
    shot_number: int
    face_consistency: float
    costume_consistency: float
    environment_consistency: float
    camera_consistency: float
    lighting_consistency: float
    motion_quality: float
    overall_score: float
    scoring_details: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class HumanReviewCreate(BaseModel):
    shot_id: str
    reviewer_name: str | None = None
    face_consistency: int = Field(ge=1, le=10)
    costume: int = Field(ge=1, le=10)
    environment: int = Field(ge=1, le=10)
    lighting: int = Field(ge=1, le=10)
    cinematography: int = Field(ge=1, le=10)
    motion: int = Field(ge=1, le=10)
    overall_quality: int = Field(ge=1, le=10)
    notes: str | None = None


class HumanReviewRead(HumanReviewCreate):
    id: str
    ai_overall_score: float | None = None
    calibration_delta: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProviderCapabilityRead(BaseModel):
    id: str
    provider: str
    model_version: str
    image_generation: bool
    image_to_video: bool
    reference_handling: bool
    seed_support: bool
    available_resolutions: list = Field(default_factory=list)
    max_references: int
    cost_per_generation: float
    notes: str | None = None

    model_config = {"from_attributes": True}


class EvaluationDashboardRead(BaseModel):
    benchmark_count: int
    latest_runs: list[BenchmarkRunRead]
    average_overall_score: float
    human_ai_calibration_delta: float
    north_star: dict


class ExperimentPlanRead(BaseModel):
    objective: str
    variant_count: int
    variants: list[dict]


class AutonomousBatchRead(BaseModel):
    provider: str
    runs: list[BenchmarkRunRead]
    summary: dict


class GeneLearningRead(BaseModel):
    baseline: float
    interpretation: str
    gene_impacts: dict


class ProviderDNARead(BaseModel):
    provider: str
    sample_count: int
    likes: list[str]
    dislikes: list[str]
    learned_observations: list[str]
    average_scores: dict


class ResearchReportRead(BaseModel):
    title: str
    generation_count: int
    dataset_records: int
    benchmark_runs: int
    acceptance_rate: float
    average_face_score: float
    average_overall_score: float
    discoveries: list[str]
    north_star: str


class BenchmarkGateRead(BaseModel):
    baseline_run_id: str
    candidate_run_id: str
    baseline_overall: float
    candidate_overall: float
    delta: float
    passes_gate: bool
    rule: str


class DebateRequest(BaseModel):
    prompt: str
    context: dict = Field(default_factory=dict)


class DebateRead(BaseModel):
    prompt: str
    context: dict
    votes: list[dict]
    decision: str
    final_recommendation: str


class SymbolicPromptRequest(BaseModel):
    components: dict = Field(default_factory=dict)


class SymbolicPromptRead(BaseModel):
    symbols: dict
    compact_language: str
    compiler_note: str
