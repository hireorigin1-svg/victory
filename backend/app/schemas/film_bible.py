from datetime import datetime

from pydantic import BaseModel, Field


class FilmBibleBase(BaseModel):
    project_name: str = "Default Project"
    characters: list[dict] = Field(default_factory=list)
    relationships: list[dict] = Field(default_factory=list)
    locations: list[dict] = Field(default_factory=list)
    costumes: list[dict] = Field(default_factory=list)
    weapons: list[dict] = Field(default_factory=list)
    vehicles: list[dict] = Field(default_factory=list)
    lighting_style: str | None = None
    color_palette: list[str] = Field(default_factory=list)
    camera_rules: list[str] = Field(default_factory=list)
    lens_package: list[str] = Field(default_factory=list)
    action_rules: list[str] = Field(default_factory=list)
    weather_rules: list[str] = Field(default_factory=list)
    timeline: list[dict] = Field(default_factory=list)
    continuity_rules: list[str] = Field(default_factory=list)


class FilmBibleCreate(FilmBibleBase):
    pass


class FilmBibleUpdate(BaseModel):
    project_name: str | None = None
    characters: list[dict] | None = None
    relationships: list[dict] | None = None
    locations: list[dict] | None = None
    costumes: list[dict] | None = None
    weapons: list[dict] | None = None
    vehicles: list[dict] | None = None
    lighting_style: str | None = None
    color_palette: list[str] | None = None
    camera_rules: list[str] | None = None
    lens_package: list[str] | None = None
    action_rules: list[str] | None = None
    weather_rules: list[str] | None = None
    timeline: list[dict] | None = None
    continuity_rules: list[str] | None = None


class FilmBibleRead(FilmBibleBase):
    id: str
    version_history: list = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
