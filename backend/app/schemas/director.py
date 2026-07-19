from pydantic import BaseModel, Field

from app.schemas.shot import ContinuityReport, ShotRead


class DirectorRunRequest(BaseModel):
    script: str = Field(min_length=1)
    user_instruction: str = Field(min_length=1)
    max_attempts: int = Field(default=5, ge=1, le=5)


class DirectorRunResponse(BaseModel):
    scene_id: str
    shot: ShotRead
    prompt: str
    explanation: list[dict]
    warnings: list[str]
    quality_report: ContinuityReport
    movie_state: dict
