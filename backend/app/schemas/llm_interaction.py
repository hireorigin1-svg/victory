from datetime import datetime

from pydantic import BaseModel, Field


class LLMInteractionRead(BaseModel):
    id: str
    workflow_id: str | None = None
    shot_id: str | None = None
    provider: str
    model: str | None = None
    purpose: str
    request_context: dict = Field(default_factory=dict)
    instruction: str
    response_text: str
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
