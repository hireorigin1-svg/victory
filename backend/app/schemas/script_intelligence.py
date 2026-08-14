from pydantic import BaseModel, Field


class ScriptAnalysisRequest(BaseModel):
    title: str = "Untitled Script"
    script_text: str = Field(min_length=20)


class ScriptSceneBreakdown(BaseModel):
    scene_number: int
    heading: str
    location: str
    time_of_day: str | None = None
    summary: str
    characters: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    emotional_beat: str
    visual_style: str


class ScriptCharacterBreakdown(BaseModel):
    name: str
    dialogue_lines: int = 0
    first_scene: int | None = None
    description: str = ""
    body_language: str = ""


class ScriptAnalysisResponse(BaseModel):
    title: str
    source: str = "grounded_screenplay_parser"
    fallback_used: bool = False
    genre: str
    logline: str
    summary: str
    scene_count: int
    character_count: int
    characters: list[ScriptCharacterBreakdown]
    locations: list[str]
    props: list[str]
    themes: list[str]
    continuity_rules: list[str]
    scenes: list[ScriptSceneBreakdown]
    warnings: list[str] = Field(default_factory=list)


class StoryboardRequest(BaseModel):
    title: str = "Untitled Script"
    script_text: str = Field(min_length=20)
    style: str = "devotional cinematic realism"
    max_panels: int = Field(default=12, ge=1, le=40)
    create_project_records: bool = False


class StoryboardPanel(BaseModel):
    panel_number: int
    scene_number: int
    heading: str
    shot_type: str
    camera: str
    lighting: str
    characters: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    action: str
    image_prompt: str
    continuity_notes: list[str] = Field(default_factory=list)
    created_scene_id: str | None = None
    created_shot_id: str | None = None


class StoryboardResponse(BaseModel):
    title: str
    source: str = "grounded_screenplay_parser"
    fallback_used: bool = False
    panel_count: int
    panels: list[StoryboardPanel]
    warnings: list[str] = Field(default_factory=list)
