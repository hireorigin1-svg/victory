from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models.camera import CameraProfile
from app.models.character import Character
from app.models.environment import Environment
from app.models.film_bible import FilmBible
from app.models.prop import Prop
from app.models.scene import Scene
from app.models.shot import Shot
from app.models.visual_memory import VisualMemory
from app.repositories.cameras import CameraRepository
from app.repositories.characters import CharacterRepository
from app.repositories.environments import EnvironmentRepository
from app.repositories.film_bibles import FilmBibleRepository
from app.repositories.props import PropRepository
from app.repositories.scenes import SceneRepository
from app.repositories.shots import ShotRepository
from app.repositories.visual_memories import VisualMemoryRepository


@dataclass(frozen=True)
class CompilerRule:
    priority: int
    source: str
    key: str
    value: Any
    explanation: str


class PromptCompiler:
    priority_names = {
        1: "previous_approved_visual_memory",
        2: "film_bible",
        3: "character_database",
        4: "environment_database",
        5: "user_instruction",
    }

    conflict_terms = {
        "costume": ["costume", "clothes", "robe", "armor", "dress"],
        "lighting": ["lighting", "dark", "night", "sunset", "sunrise", "dawn"],
        "weather": ["weather", "rain", "storm", "snow", "cloudy", "clear"],
        "camera": ["camera", "lens", "angle", "dolly", "handheld", "closeup"],
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def compile(
        self,
        scene_id: str,
        user_instruction: str,
        shot_id: str | None = None,
        camera_id: str | None = None,
    ) -> tuple[str, dict, list[dict], list[str]]:
        scene = SceneRepository(self.db).get(scene_id)
        if not scene:
            raise ValueError("Scene not found")

        shot = ShotRepository(self.db).get(shot_id) if shot_id else None
        previous_shot = self._previous_shot(scene, shot)
        film_bible = FilmBibleRepository(self.db).get_singleton()
        visual_memory = self._visual_memory(previous_shot, scene)
        environment = self._environment(scene, shot)
        camera = self._camera(camera_id, shot)
        characters = self._characters(scene)
        props = self._props(scene)

        rules = self._build_rules(
            film_bible=film_bible,
            visual_memory=visual_memory,
            scene=scene,
            previous_shot=previous_shot,
            characters=characters,
            environment=environment,
            camera=camera,
            props=props,
            user_instruction=user_instruction,
        )
        warnings = self._detect_conflicts(rules, user_instruction)
        components = self._materialize_components(rules)
        prompt = self._render_prompt(components, warnings)
        explanation = [rule.__dict__ for rule in rules]
        return prompt, components, explanation, warnings

    def _build_rules(
        self,
        film_bible: FilmBible | None,
        visual_memory: VisualMemory | None,
        scene: Scene,
        previous_shot: Shot | None,
        characters: list[Character],
        environment: Environment | None,
        camera: CameraProfile | None,
        props: list[Prop],
        user_instruction: str,
    ) -> list[CompilerRule]:
        rules: list[CompilerRule] = []

        if visual_memory:
            rules.extend(
                self._rule(1, "Visual Memory", key, value, "Ground truth extracted from the previous approved image.")
                for key, value in visual_memory.state.items()
                if value not in (None, "", [], {})
            )
        elif previous_shot and previous_shot.vision_analysis:
            rules.extend(
                self._rule(1, "Previous Shot", key, value, "Ground truth from previous approved shot analysis.")
                for key, value in previous_shot.vision_analysis.items()
                if value not in (None, "", [], {})
            )

        if film_bible:
            bible_values = {
                "film_lighting_style": film_bible.lighting_style,
                "color_palette": film_bible.color_palette,
                "camera_rules": film_bible.camera_rules,
                "lens_package": film_bible.lens_package,
                "action_rules": film_bible.action_rules,
                "weather_rules": film_bible.weather_rules,
                "continuity_rules": film_bible.continuity_rules,
                "film_timeline": film_bible.timeline,
            }
            rules.extend(
                self._rule(2, "Film Bible", key, value, "Film Bible rule loaded before all database and user inputs.")
                for key, value in bible_values.items()
                if value not in (None, "", [], {})
            )

        for character in characters:
            rules.append(
                self._rule(
                    3,
                    "Character Database",
                    f"character:{character.name}",
                    {
                        "face": character.face,
                        "hair": character.hair,
                        "skin": character.skin,
                        "height": character.height,
                        "body": character.body,
                        "clothes": character.clothes,
                        "accessories": character.accessories,
                        "voice": character.voice,
                        "walking_style": character.walking_style,
                        "expressions": character.expressions,
                    },
                    f"Canonical identity record for {character.name}.",
                )
            )

        if environment:
            rules.append(
                self._rule(
                    4,
                    "Environment Database",
                    "environment",
                    {
                        "location": environment.location,
                        "architecture": environment.architecture,
                        "lighting": environment.lighting,
                        "weather": environment.weather,
                        "time": environment.time,
                        "props": environment.props,
                        "background_assets": environment.background_assets,
                    },
                    "Canonical environment continuity record.",
                )
            )

        if camera:
            rules.append(
                self._rule(
                    4,
                    "Camera Database",
                    "camera",
                    {
                        "name": camera.name,
                        "lens": camera.lens,
                        "camera_angle": camera.camera_angle,
                        "movement": camera.movement,
                        "aspect_ratio": camera.aspect_ratio,
                        "depth_of_field": camera.depth_of_field,
                        "fps": camera.fps,
                        "motion_blur": camera.motion_blur,
                        "film_look": camera.film_look,
                    },
                    "Camera profile selected for this shot.",
                )
            )

        if props:
            rules.append(
                self._rule(
                    4,
                    "Prop Database",
                    "props",
                    [
                        {
                            "name": prop.name,
                            "category": prop.category,
                            "description": prop.description,
                            "position": prop.position,
                            "damage_state": prop.damage_state,
                        }
                        for prop in props
                    ],
                    "Canonical prop state for this scene.",
                )
            )

        rules.extend(
            [
                self._rule(4, "Scene Database", "scene", f"Scene {scene.scene_number}: {scene.script}", "Scene script and number."),
                self._rule(4, "Scene Database", "timeline", scene.timeline, "Scene timeline state."),
                self._rule(5, "User Instruction", "requested_action", user_instruction, "Lowest-priority shot action request."),
            ]
        )
        return [rule for rule in rules if rule.value not in (None, "", [], {})]

    def _materialize_components(self, rules: list[CompilerRule]) -> dict:
        components: dict[str, Any] = {
            "priority_order": self.priority_names,
            "previous_approved_shot": {},
            "film_bible": {},
            "character_database": {},
            "environment_database": {},
            "scene": {},
            "user_instruction": None,
        }
        for rule in rules:
            bucket = self.priority_names[rule.priority]
            if rule.priority == 5:
                components["user_instruction"] = rule.value
            else:
                components.setdefault(bucket, {})[rule.key] = rule.value
        return components

    def _detect_conflicts(self, rules: list[CompilerRule], user_instruction: str) -> list[str]:
        warnings: list[str] = []
        lower_instruction = user_instruction.lower()
        locked_keys = {
            rule.key.lower(): rule
            for rule in rules
            if rule.priority in (1, 2, 3, 4) and rule.value not in (None, "", [], {})
        }
        for domain, terms in self.conflict_terms.items():
            if not any(term in lower_instruction for term in terms):
                continue
            for key, rule in locked_keys.items():
                if domain in key or domain in str(rule.value).lower():
                    warnings.append(
                        f"Potential continuity conflict: user instruction mentions {domain}, but {rule.source} locks {rule.key}."
                    )
                    break
        return warnings

    def _render_prompt(self, components: dict, warnings: list[str]) -> str:
        lines = [
            "Generate one optimized cinematic prompt using this resolved continuity state.",
            "Apply priority order: previous approved visual memory > Film Bible > character database > environment/camera/prop database > user instruction.",
        ]
        if warnings:
            lines.append("Director warning: resolve conflicts before generation unless explicit approval is recorded.")
        for section in [
            "previous_approved_visual_memory",
            "film_bible",
            "character_database",
            "environment_database",
            "scene",
        ]:
            value = components.get(section)
            if value:
                lines.append(f"{section}: {value}")
        lines.append(f"user_instruction: {components.get('user_instruction')}")
        lines.append("Output style: precise cinematic image/video prompt; no alternate story beats; preserve locked continuity.")
        return "\n".join(lines)

    def _rule(self, priority: int, source: str, key: str, value: Any, explanation: str) -> CompilerRule:
        return CompilerRule(priority=priority, source=source, key=key, value=value, explanation=explanation)

    def _previous_shot(self, scene: Scene, shot: Shot | None) -> Shot | None:
        repo = ShotRepository(self.db)
        if shot and shot.previous_shot_id:
            return repo.get(shot.previous_shot_id)
        if shot:
            return repo.get_previous_approved(scene.id, shot.shot_number)
        return None

    def _visual_memory(self, previous_shot: Shot | None, scene: Scene) -> VisualMemory | None:
        repo = VisualMemoryRepository(self.db)
        if previous_shot:
            return repo.get_for_shot(previous_shot.id)
        return repo.latest_for_scene(scene.id)

    def _environment(self, scene: Scene, shot: Shot | None) -> Environment | None:
        environment_id = shot.environment_id if shot and shot.environment_id else scene.environment_id
        return EnvironmentRepository(self.db).get(environment_id) if environment_id else None

    def _camera(self, camera_id: str | None, shot: Shot | None) -> CameraProfile | None:
        selected_id = camera_id or (shot.camera_id if shot else None)
        return CameraRepository(self.db).get(selected_id) if selected_id else None

    def _characters(self, scene: Scene) -> list[Character]:
        repo = CharacterRepository(self.db)
        return [character for item_id in scene.character_ids if (character := repo.get(item_id))]

    def _props(self, scene: Scene) -> list[Prop]:
        repo = PropRepository(self.db)
        return [prop for item_id in scene.prop_ids if (prop := repo.get(item_id))]
