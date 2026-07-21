from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.shot import ContinuityReport, ShotRead


class DirectorOSV2RunRequest(BaseModel):
    script: str = Field(min_length=1)
    user_instruction: str = Field(min_length=1)
    scene_id: str | None = None
    provider: str = "higgsfield"
    max_attempts: int = Field(default=5, ge=1, le=5)
    claude_review_below: float = Field(default=95, ge=0, le=100)


class DirectorOSV2RunResponse(BaseModel):
    scene_id: str
    shot: ShotRead
    blueprint_id: str
    knowledge_packet_id: str
    translation_id: str
    blueprint: dict
    knowledge_packet: dict
    gpt_prompt: str
    claude_review: dict | None = None
    translated_prompt: str
    confidence_score: float
    provider: str
    evaluation: ContinuityReport
    decision: str
    learning_record: dict
    created_at: datetime | None = None
