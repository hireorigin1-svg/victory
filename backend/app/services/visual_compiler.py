from sqlalchemy.orm import Session

from app.repositories.film_bibles import FilmBibleRepository
from app.repositories.shots import ShotRepository
from app.repositories.visual_intelligence import CinematographyStyleRepository, VisualPlanRepository


class VisualCompiler:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.plans = VisualPlanRepository(db)

    def compile_plan(self, shot_id: str, style_name: str | None = None):
        shot = ShotRepository(self.db).get(shot_id)
        if not shot:
            raise ValueError("Shot not found")
        bible = FilmBibleRepository(self.db).get_singleton()
        style = CinematographyStyleRepository(self.db).get_by_name(style_name) if style_name else None
        camera_rules = style.camera_rules if style else {}
        lighting_rules = style.lighting_rules if style else {}
        composition_rules = style.composition_rules if style else {}
        plan = {
            "shot_id": shot.id,
            "character_blocking": [
                {
                    "position": "inherit from movie state unless script changes",
                    "pose": shot.pose or "script-derived",
                    "emotion": shot.emotion or "script-derived",
                }
            ],
            "camera": {
                "lens": camera_rules.get("lens") or "35mm",
                "angle": camera_rules.get("angle") or "story motivated",
                "movement": camera_rules.get("movement") or "stable cinematic movement",
            },
            "lighting": {
                "style": lighting_rules.get("style") or (bible.lighting_style if bible else None),
                "direction": lighting_rules.get("direction") or "motivated key light",
                "contrast": lighting_rules.get("contrast") or "controlled",
            },
            "composition": {
                "rule_of_thirds": composition_rules.get("rule_of_thirds", True),
                "negative_space": composition_rules.get("negative_space", "balanced"),
                "depth_layers": composition_rules.get("depth_layers", 3),
            },
            "color_palette": bible.color_palette if bible else [],
            "motion": {"subject": shot.user_instruction, "camera": camera_rules.get("movement")},
            "constraints": [
                "Preserve visual memory as ground truth.",
                "Use selected reference segments for identity, costume, and environment.",
            ],
        }
        existing = self.plans.get_for_shot(shot.id)
        return self.plans.update(existing, plan) if existing else self.plans.create(plan)
