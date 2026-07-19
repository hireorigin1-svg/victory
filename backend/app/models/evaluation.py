from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class BenchmarkProject(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "benchmark_projects"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    character_count: Mapped[int] = mapped_column(Integer, default=1)
    environment_count: Mapped[int] = mapped_column(Integer, default=1)
    shot_count: Mapped[int] = mapped_column(Integer, default=50)
    scenario: Mapped[str] = mapped_column(String(120), default="sequential_continuity")
    spec: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class BenchmarkRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "benchmark_runs"

    benchmark_id: Mapped[str] = mapped_column(ForeignKey("benchmark_projects.id"), index=True)
    provider: Mapped[str] = mapped_column(String(120), default="mock")
    model_version: Mapped[str | None] = mapped_column(String(120))
    pipeline_version: Mapped[str] = mapped_column(String(120), default="local")
    status: Mapped[str] = mapped_column(String(80), default="completed")
    summary_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    total_cost: Mapped[float] = mapped_column(Float, default=0)
    total_latency_ms: Mapped[float] = mapped_column(Float, default=0)


class BenchmarkShotScore(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "benchmark_shot_scores"

    benchmark_run_id: Mapped[str] = mapped_column(ForeignKey("benchmark_runs.id"), index=True)
    shot_id: Mapped[str | None] = mapped_column(ForeignKey("shots.id"), index=True)
    shot_number: Mapped[int] = mapped_column(Integer, default=1)
    face_consistency: Mapped[float] = mapped_column(Float, default=100)
    costume_consistency: Mapped[float] = mapped_column(Float, default=100)
    environment_consistency: Mapped[float] = mapped_column(Float, default=100)
    camera_consistency: Mapped[float] = mapped_column(Float, default=100)
    lighting_consistency: Mapped[float] = mapped_column(Float, default=100)
    motion_quality: Mapped[float] = mapped_column(Float, default=100)
    overall_score: Mapped[float] = mapped_column(Float, default=100)
    scoring_details: Mapped[dict] = mapped_column(JSON, default=dict)


class HumanReview(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "human_reviews"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    reviewer_name: Mapped[str | None] = mapped_column(String(120))
    face_consistency: Mapped[int] = mapped_column(Integer)
    costume: Mapped[int] = mapped_column(Integer)
    environment: Mapped[int] = mapped_column(Integer)
    lighting: Mapped[int] = mapped_column(Integer)
    cinematography: Mapped[int] = mapped_column(Integer)
    motion: Mapped[int] = mapped_column(Integer)
    overall_quality: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    ai_overall_score: Mapped[float | None] = mapped_column(Float)
    calibration_delta: Mapped[float | None] = mapped_column(Float)


class ProviderCapability(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "provider_capabilities"

    provider: Mapped[str] = mapped_column(String(120), index=True)
    model_version: Mapped[str] = mapped_column(String(120), index=True)
    image_generation: Mapped[bool] = mapped_column(Boolean, default=True)
    image_to_video: Mapped[bool] = mapped_column(Boolean, default=False)
    reference_handling: Mapped[bool] = mapped_column(Boolean, default=False)
    seed_support: Mapped[bool] = mapped_column(Boolean, default=False)
    available_resolutions: Mapped[list] = mapped_column(JSON, default=list)
    max_references: Mapped[int] = mapped_column(Integer, default=1)
    cost_per_generation: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str | None] = mapped_column(Text)


class GenerationDatasetRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "generation_dataset_records"

    experiment_id: Mapped[str | None] = mapped_column(ForeignKey("generation_experiments.id"), index=True)
    shot_id: Mapped[str | None] = mapped_column(ForeignKey("shots.id"), index=True)
    provider: Mapped[str] = mapped_column(String(120), default="mock")
    model_version: Mapped[str | None] = mapped_column(String(120))
    inputs: Mapped[dict] = mapped_column(JSON, default=dict)
    outputs: Mapped[dict] = mapped_column(JSON, default=dict)
    scores: Mapped[dict] = mapped_column(JSON, default=dict)
    human_ratings: Mapped[dict] = mapped_column(JSON, default=dict)
    accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    cost: Mapped[float] = mapped_column(Float, default=0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0)
