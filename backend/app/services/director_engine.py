from sqlalchemy.orm import Session

from app.models.shot import ShotStatus
from app.repositories.characters import CharacterRepository
from app.repositories.scenes import SceneRepository
from app.repositories.shots import ShotRepository
from app.services.embedding_registry import CharacterEmbeddingRegistry
from app.repositories.embeddings import CharacterEmbeddingRepository
from app.services.movie_state import MovieStateService
from app.services.prompt_compiler import PromptCompiler
from app.services.quality_gate import QualityGate
from app.services.visual_memory import VisualMemoryService


class DirectorEngine:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.scenes = SceneRepository(db)
        self.shots = ShotRepository(db)

    def run(self, script: str, user_instruction: str, max_attempts: int = 5) -> dict:
        scene = self._plan_scene(script)
        previous = self.shots.get_previous_approved(scene.id, 10**9)
        shot_number = len(self.shots.list_for_scene(scene.id)) + 1
        prompt, components, explanation, warnings = PromptCompiler(self.db).compile(
            scene_id=scene.id,
            user_instruction=user_instruction,
        )
        shot = self.shots.create(
            {
                "scene_id": scene.id,
                "shot_number": shot_number,
                "user_instruction": user_instruction,
                "prompt": prompt,
                "prompt_components": components,
                "director_explanation": explanation,
                "continuity_warnings": warnings,
                "previous_shot_id": previous.id if previous else None,
                "status": ShotStatus.needs_director_approval if warnings else ShotStatus.queued,
            }
        )

        if warnings:
            report = QualityGate(self.shots).checker.compare(previous, shot)
            self.shots.update(
                shot,
                {
                    "continuity_score": report.overall_continuity_score,
                    "status": ShotStatus.needs_director_approval,
                    "rejection_reason": "Director approval required before generation because continuity warnings were raised.",
                },
            )
        else:
            shot = self.shots.update(shot, {"vision_analysis": {
                "face": "pending provider extraction",
                "hair": "pending provider extraction",
                "clothes": "pending provider extraction",
                "environment": shot.environment_id,
                "camera": shot.camera_id,
                "lighting": shot.lighting,
                "pose": shot.pose,
                "props": [],
            }})
            report = QualityGate(self.shots).evaluate(shot, previous, max_attempts=max_attempts)

        visual_memory = None
        movie_state = MovieStateService(self.db).get_or_create()
        if shot.status == ShotStatus.approved:
            visual_memory = VisualMemoryService(self.db).capture_approved_shot(shot)
            movie_state = MovieStateService(self.db).apply_approved_shot(shot, visual_memory.state)
            self._register_character_embeddings(scene.character_ids, shot, visual_memory.state)

        return {
            "scene_id": scene.id,
            "shot": shot,
            "prompt": prompt,
            "explanation": explanation,
            "warnings": warnings,
            "quality_report": report,
            "movie_state": movie_state.state,
        }

    def approve_shot(self, shot_id: str) -> dict:
        shot = self.shots.get(shot_id)
        if not shot:
            raise ValueError("Shot not found")
        shot = self.shots.update(shot, {"status": ShotStatus.approved})
        visual_memory = VisualMemoryService(self.db).capture_approved_shot(shot)
        movie_state = MovieStateService(self.db).apply_approved_shot(shot, visual_memory.state)
        scene = self.scenes.get(shot.scene_id)
        if scene:
            self._register_character_embeddings(scene.character_ids, shot, visual_memory.state)
        return {"shot": shot, "visual_memory": visual_memory, "movie_state": movie_state}

    def _plan_scene(self, script: str):
        existing = self.scenes.get_by_number(1)
        if existing:
            return self.scenes.update(existing, {"script": script})
        return self.scenes.create(
            {
                "scene_number": 1,
                "script": script,
                "character_ids": [],
                "prop_ids": [],
                "approved_shot_ids": [],
            }
        )

    def _register_character_embeddings(self, character_ids: list[str], shot, memory: dict) -> None:
        character_repo = CharacterRepository(self.db)
        registry = CharacterEmbeddingRegistry(CharacterEmbeddingRepository(self.db))
        for character_id in character_ids:
            character = character_repo.get(character_id)
            if character:
                registry.register_from_memory(character, shot, memory)
