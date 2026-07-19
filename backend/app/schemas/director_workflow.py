from datetime import datetime

from pydantic import BaseModel, Field


class DirectorWorkflowStart(BaseModel):
    director_instruction: str = Field(min_length=1)
    scene_id: str | None = None
    shot_number: int = Field(default=1, ge=1)
    camera_id: str | None = None
    environment_id: str | None = None
    lighting: str | None = None
    emotion: str | None = None
    pose: str | None = None


class DirectorWorkflowUpload(BaseModel):
    image_url: str | None = None
    video_url: str | None = None


class DirectorWorkflowReview(BaseModel):
    approved: bool
    image_url: str | None = None
    video_url: str | None = None
    reasons: list[str] = Field(default_factory=list)


class DirectorWorkflowEvaluation(BaseModel):
    face: float
    costume: float
    environment: float
    lighting: float
    camera: float
    overall: float
    decision: str
    notes: list[str] = Field(default_factory=list)


class DirectorWorkflowRead(BaseModel):
    id: str
    shot_id: str
    director_instruction: str
    gpt_prompt: str | None = None
    claude_prompt: str | None = None
    higgsfield_prompt: str | None = None
    uploaded_image_url: str | None = None
    uploaded_video_url: str | None = None
    approval_status: str
    review_reasons: list = Field(default_factory=list)
    improved_gpt_prompt: str | None = None
    improved_claude_prompt: str | None = None
    llm_context: dict = Field(default_factory=dict)
    workflow_events: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
