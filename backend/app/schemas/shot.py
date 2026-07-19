from datetime import datetime

from pydantic import BaseModel, Field

from app.models.shot import ShotStatus


class ShotBase(BaseModel):
    scene_id: str
    shot_number: int = Field(ge=1)
    user_instruction: str = Field(min_length=1)
    camera_id: str | None = None
    environment_id: str | None = None
    previous_shot_id: str | None = None
    next_shot_id: str | None = None
    lighting: str | None = None
    emotion: str | None = None
    pose: str | None = None


class ShotCreate(ShotBase):
    pass


class ShotUpdate(BaseModel):
    user_instruction: str | None = None
    prompt: str | None = None
    generated_image: str | None = None
    generated_video: str | None = None
    approved_image: str | None = None
    approved_video: str | None = None
    camera_id: str | None = None
    environment_id: str | None = None
    previous_shot_id: str | None = None
    next_shot_id: str | None = None
    lighting: str | None = None
    emotion: str | None = None
    pose: str | None = None
    quality_score: float | None = Field(default=None, ge=0, le=100)
    continuity_score: float | None = Field(default=None, ge=0, le=100)
    status: ShotStatus | None = None
    vision_analysis: dict | None = None
    rejection_reason: str | None = None


class ShotRead(ShotBase):
    id: str
    prompt: str | None = None
    generated_image: str | None = None
    generated_video: str | None = None
    approved_image: str | None = None
    approved_video: str | None = None
    quality_score: float | None = None
    continuity_score: float | None = None
    status: ShotStatus
    prompt_components: dict = Field(default_factory=dict)
    vision_analysis: dict = Field(default_factory=dict)
    rejection_reason: str | None = None
    generation_attempts: int = 0
    director_explanation: list = Field(default_factory=list)
    continuity_warnings: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromptCompileRequest(BaseModel):
    scene_id: str
    user_instruction: str
    shot_id: str | None = None
    camera_id: str | None = None


class PromptCompileResponse(BaseModel):
    prompt: str
    components: dict
    explanation: list[dict] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ContinuityReport(BaseModel):
    face_similarity: float
    hair_similarity: float = 100
    body_similarity: float = 100
    clothing_similarity: float
    environment_similarity: float
    lighting_similarity: float
    pose_similarity: float = 100
    props_similarity: float = 100
    camera_similarity: float
    overall_continuity_score: float
    decision: ShotStatus
    notes: list[str]
