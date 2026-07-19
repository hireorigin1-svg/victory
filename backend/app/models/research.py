from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PromptGenome(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "prompt_genomes"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    experiment_id: Mapped[str | None] = mapped_column(ForeignKey("generation_experiments.id"), index=True)
    prompt_hash: Mapped[str] = mapped_column(String(64), index=True)
    genes: Mapped[dict] = mapped_column(JSON, default=dict)


class ProviderBehaviorRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "provider_behavior_records"

    provider: Mapped[str] = mapped_column(String(120), index=True)
    provider_model: Mapped[str | None] = mapped_column(String(120), index=True)
    provider_version: Mapped[str | None] = mapped_column(String(120), index=True)
    prompt_genome_id: Mapped[str | None] = mapped_column(ForeignKey("prompt_genomes.id"), index=True)
    experiment_id: Mapped[str | None] = mapped_column(ForeignKey("generation_experiments.id"), index=True)
    reference_strength: Mapped[float | None] = mapped_column(Float)
    face_score: Mapped[float | None] = mapped_column(Float)
    camera_score: Mapped[float | None] = mapped_column(Float)
    lighting_score: Mapped[float | None] = mapped_column(Float)
    environment_score: Mapped[float | None] = mapped_column(Float)
    costume_score: Mapped[float | None] = mapped_column(Float)
    learned_observations: Mapped[list] = mapped_column(JSON, default=list)


class ABTestGroup(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ab_test_groups"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    provider: Mapped[str] = mapped_column(String(120), default="mock")
    variants: Mapped[list] = mapped_column(JSON, default=list)
    winning_experiment_id: Mapped[str | None] = mapped_column(ForeignKey("generation_experiments.id"))
    winning_variant: Mapped[str | None] = mapped_column(String(20))
    winner_score: Mapped[float | None] = mapped_column(Float)


class CharacterIdentityProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "character_identity_profiles"

    character_id: Mapped[str] = mapped_column(ForeignKey("characters.id"), unique=True, index=True)
    approved_image_count: Mapped[int] = mapped_column(Integer, default=0)
    canonical_vector: Mapped[list] = mapped_column(JSON, default=list)
    profile: Mapped[dict] = mapped_column(JSON, default=dict)
    stability_score: Mapped[float | None] = mapped_column(Float)


class SceneSimulation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scene_simulations"

    scene_id: Mapped[str] = mapped_column(ForeignKey("scenes.id"), index=True)
    expected_state: Mapped[dict] = mapped_column(JSON, default=dict)
    detected_conflicts: Mapped[list] = mapped_column(JSON, default=list)
    recommended_prompt_constraints: Mapped[list] = mapped_column(JSON, default=list)
    safe_to_generate: Mapped[bool] = mapped_column(Boolean, default=True)


class ProductionMetric(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "production_metrics"

    scope: Mapped[str] = mapped_column(String(120), index=True)
    metric_name: Mapped[str] = mapped_column(String(120), index=True)
    metric_value: Mapped[float] = mapped_column(Float)
    dimensions: Mapped[dict] = mapped_column(JSON, default=dict)
    notes: Mapped[str | None] = mapped_column(Text)
