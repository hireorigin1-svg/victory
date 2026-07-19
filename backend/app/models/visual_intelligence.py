from sqlalchemy import Boolean, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class VisualSceneGraph(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "visual_scene_graphs"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    source_image: Mapped[str | None] = mapped_column(String(1024))
    entities: Mapped[list] = mapped_column(JSON, default=list)
    relations: Mapped[list] = mapped_column(JSON, default=list)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    extractor: Mapped[str] = mapped_column(String(80), default="gpt-vision-ready")


class PromptAST(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "prompt_asts"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    prompt_hash: Mapped[str] = mapped_column(String(64), index=True)
    ast: Mapped[dict] = mapped_column(JSON, default=dict)


class VisualPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "visual_plans"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), unique=True, index=True)
    character_blocking: Mapped[list] = mapped_column(JSON, default=list)
    camera: Mapped[dict] = mapped_column(JSON, default=dict)
    lighting: Mapped[dict] = mapped_column(JSON, default=dict)
    composition: Mapped[dict] = mapped_column(JSON, default=dict)
    color_palette: Mapped[list] = mapped_column(JSON, default=list)
    motion: Mapped[dict] = mapped_column(JSON, default=dict)
    constraints: Mapped[list] = mapped_column(JSON, default=list)


class ReferenceAsset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reference_assets"

    shot_id: Mapped[str | None] = mapped_column(ForeignKey("shots.id"), index=True)
    character_id: Mapped[str | None] = mapped_column(ForeignKey("characters.id"), index=True)
    environment_id: Mapped[str | None] = mapped_column(ForeignKey("environments.id"), index=True)
    image_url: Mapped[str] = mapped_column(String(1024))
    approved: Mapped[bool] = mapped_column(Boolean, default=True)
    quality_score: Mapped[float | None] = mapped_column(Float)


class ReferenceSegment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reference_segments"

    reference_asset_id: Mapped[str] = mapped_column(ForeignKey("reference_assets.id"), index=True)
    segment_type: Mapped[str] = mapped_column(String(80), index=True)
    crop_url: Mapped[str | None] = mapped_column(String(1024))
    embedding: Mapped[list] = mapped_column(JSON, default=list)
    features: Mapped[dict] = mapped_column(JSON, default=dict)
    quality_score: Mapped[float | None] = mapped_column(Float)


class ReferenceSelection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reference_selections"

    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    requested_continuity: Mapped[dict] = mapped_column(JSON, default=dict)
    selected_segments: Mapped[list] = mapped_column(JSON, default=list)
    rationale: Mapped[list] = mapped_column(JSON, default=list)


class VisualDiff(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "visual_diffs"

    baseline_shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    candidate_shot_id: Mapped[str] = mapped_column(ForeignKey("shots.id"), index=True)
    changes: Mapped[list] = mapped_column(JSON, default=list)
    corrections: Mapped[list] = mapped_column(JSON, default=list)
    overall_delta_score: Mapped[float | None] = mapped_column(Float)


class FailureCluster(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "failure_clusters"

    cluster_type: Mapped[str] = mapped_column(String(120), index=True)
    experiment_ids: Mapped[list] = mapped_column(JSON, default=list)
    common_causes: Mapped[list] = mapped_column(JSON, default=list)
    recommended_actions: Mapped[list] = mapped_column(JSON, default=list)


class CinematographyStyle(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cinematography_styles"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    scenario: Mapped[str] = mapped_column(String(120), default="general")
    camera_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    lighting_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    composition_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    notes: Mapped[str | None] = mapped_column(Text)
