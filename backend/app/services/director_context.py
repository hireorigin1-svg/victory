from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.camera import CameraProfile
from app.models.character import Character
from app.models.critic_review import CriticReview
from app.models.director_workflow import DirectorWorkflow
from app.models.environment import Environment
from app.models.evaluation import HumanReview
from app.models.film_bible import FilmBible
from app.models.generation_experiment import GenerationExperiment
from app.models.movie_state import MovieState
from app.models.prop import Prop
from app.models.research import PromptGenome, ProviderBehaviorRecord
from app.models.scene import Scene
from app.models.shot import Shot, ShotStatus
from app.models.visual_memory import VisualMemory


class DirectorContextBuilder:
    def __init__(self, db: Session) -> None:
        self.db = db

    def build(self, *, scene: Scene, shot: Shot, compiler_context: dict[str, Any]) -> dict[str, Any]:
        approved_shots = self._approved_shots(scene.id)
        rejected_shots = self._rejected_shots(scene.id)
        recent_workflows = self._recent_workflows()
        experiments = self._recent_experiments()
        return {
            "scene_id": scene.id,
            "shot_id": shot.id,
            "current": {
                "scene": self._scene(scene),
                "shot": self._shot(shot),
                "compiler": compiler_context,
            },
            "project_memory": {
                "film_bible": self._film_bible(),
                "movie_state": self._movie_state(),
                "characters": [self._character(item) for item in self._characters(scene)],
                "environment": self._environment(scene.environment_id or shot.environment_id),
                "props": [self._prop(item) for item in self._props(scene)],
                "camera": self._camera(shot.camera_id),
            },
            "continuity_memory": {
                "previous_approved_shots": [self._shot(item) for item in approved_shots],
                "latest_visual_memories": [self._visual_memory(item) for item in self._visual_memories(scene.id)],
                "rejected_shots": [self._shot(item) for item in rejected_shots],
            },
            "learning_memory": {
                "recent_director_workflows": [self._workflow(item) for item in recent_workflows],
                "recent_generation_experiments": [self._experiment(item) for item in experiments],
                "recent_prompt_genomes": [self._prompt_genome(item) for item in self._recent_prompt_genomes()],
                "provider_behavior": [self._provider_behavior(item) for item in self._provider_behavior_records()],
                "human_reviews": [self._human_review(item) for item in self._human_reviews()],
                "critic_reviews": [self._critic_review(item) for item in self._critic_reviews()],
            },
            "operating_rules": [
                "Approved visual memory is ground truth.",
                "Approved prompts and shots outrank new director text unless the director explicitly changes continuity.",
                "Rejected shots are negative examples; do not repeat their failed genes.",
                "Change only the prompt genes needed to satisfy the latest director instruction.",
                "Return Higgsfield-ready prompt text, not explanation prose, unless asked for analysis.",
            ],
        }

    def _approved_shots(self, scene_id: str) -> list[Shot]:
        return list(
            self.db.scalars(
                select(Shot)
                .where(Shot.scene_id == scene_id, Shot.status == ShotStatus.approved)
                .order_by(Shot.shot_number.desc())
                .limit(8)
            ).all()
        )

    def _rejected_shots(self, scene_id: str) -> list[Shot]:
        return list(
            self.db.scalars(
                select(Shot)
                .where(Shot.scene_id == scene_id, Shot.status == ShotStatus.rejected)
                .order_by(Shot.updated_at.desc())
                .limit(8)
            ).all()
        )

    def _recent_workflows(self) -> list[DirectorWorkflow]:
        return list(
            self.db.scalars(
                select(DirectorWorkflow).order_by(DirectorWorkflow.updated_at.desc()).limit(12)
            ).all()
        )

    def _recent_experiments(self) -> list[GenerationExperiment]:
        return list(
            self.db.scalars(
                select(GenerationExperiment)
                .order_by(GenerationExperiment.updated_at.desc())
                .limit(20)
            ).all()
        )

    def _recent_prompt_genomes(self) -> list[PromptGenome]:
        return list(
            self.db.scalars(select(PromptGenome).order_by(PromptGenome.updated_at.desc()).limit(20)).all()
        )

    def _provider_behavior_records(self) -> list[ProviderBehaviorRecord]:
        return list(
            self.db.scalars(
                select(ProviderBehaviorRecord)
                .order_by(ProviderBehaviorRecord.updated_at.desc())
                .limit(20)
            ).all()
        )

    def _human_reviews(self) -> list[HumanReview]:
        return list(self.db.scalars(select(HumanReview).order_by(HumanReview.updated_at.desc()).limit(20)).all())

    def _critic_reviews(self) -> list[CriticReview]:
        return list(self.db.scalars(select(CriticReview).order_by(CriticReview.updated_at.desc()).limit(20)).all())

    def _visual_memories(self, scene_id: str) -> list[VisualMemory]:
        return list(
            self.db.scalars(
                select(VisualMemory)
                .where(VisualMemory.scene_id == scene_id)
                .order_by(VisualMemory.updated_at.desc())
                .limit(8)
            ).all()
        )

    def _film_bible(self) -> dict[str, Any] | None:
        bible = self.db.scalars(select(FilmBible).order_by(FilmBible.created_at)).first()
        if not bible:
            return None
        return {
            "project_name": bible.project_name,
            "characters": bible.characters,
            "relationships": bible.relationships,
            "locations": bible.locations,
            "costumes": bible.costumes,
            "weapons": bible.weapons,
            "vehicles": bible.vehicles,
            "lighting_style": bible.lighting_style,
            "color_palette": bible.color_palette,
            "camera_rules": bible.camera_rules,
            "lens_package": bible.lens_package,
            "action_rules": bible.action_rules,
            "weather_rules": bible.weather_rules,
            "timeline": bible.timeline,
            "continuity_rules": bible.continuity_rules,
        }

    def _movie_state(self) -> dict[str, Any] | None:
        state = self.db.scalars(select(MovieState).order_by(MovieState.updated_at.desc())).first()
        if not state:
            return None
        return {
            "project_name": state.project_name,
            "current_scene_id": state.current_scene_id,
            "current_shot_id": state.current_shot_id,
            "state": state.state,
            "history": state.history[-8:] if state.history else [],
        }

    def _characters(self, scene: Scene) -> list[Character]:
        if not scene.character_ids:
            return list(self.db.scalars(select(Character).order_by(Character.updated_at.desc()).limit(8)).all())
        return list(self.db.scalars(select(Character).where(Character.id.in_(scene.character_ids))).all())

    def _props(self, scene: Scene) -> list[Prop]:
        if not scene.prop_ids:
            return list(self.db.scalars(select(Prop).order_by(Prop.updated_at.desc()).limit(8)).all())
        return list(self.db.scalars(select(Prop).where(Prop.id.in_(scene.prop_ids))).all())

    def _environment(self, environment_id: str | None) -> dict[str, Any] | None:
        environment = self.db.get(Environment, environment_id) if environment_id else None
        if not environment:
            return None
        return {
            "id": environment.id,
            "location": environment.location,
            "architecture": environment.architecture,
            "lighting": environment.lighting,
            "weather": environment.weather,
            "time": environment.time,
            "props": environment.props,
            "reference_images": environment.reference_images,
        }

    def _camera(self, camera_id: str | None) -> dict[str, Any] | None:
        camera = self.db.get(CameraProfile, camera_id) if camera_id else None
        if not camera:
            return None
        return {
            "id": camera.id,
            "name": camera.name,
            "lens": camera.lens,
            "camera_angle": camera.camera_angle,
            "movement": camera.movement,
            "aspect_ratio": camera.aspect_ratio,
            "depth_of_field": camera.depth_of_field,
            "fps": camera.fps,
            "motion_blur": camera.motion_blur,
            "film_look": camera.film_look,
        }

    def _scene(self, scene: Scene) -> dict[str, Any]:
        return {
            "id": scene.id,
            "scene_number": scene.scene_number,
            "script": scene.script,
            "environment_id": scene.environment_id,
            "character_ids": scene.character_ids,
            "prop_ids": scene.prop_ids,
            "timeline": scene.timeline,
            "approved_shot_ids": scene.approved_shot_ids,
        }

    def _shot(self, shot: Shot) -> dict[str, Any]:
        return {
            "id": shot.id,
            "scene_id": shot.scene_id,
            "shot_number": shot.shot_number,
            "user_instruction": shot.user_instruction,
            "prompt": shot.prompt,
            "generated_image": shot.generated_image,
            "generated_video": shot.generated_video,
            "approved_image": shot.approved_image,
            "approved_video": shot.approved_video,
            "lighting": shot.lighting,
            "emotion": shot.emotion,
            "pose": shot.pose,
            "quality_score": shot.quality_score,
            "continuity_score": shot.continuity_score,
            "status": str(shot.status),
            "prompt_components": shot.prompt_components,
            "vision_analysis": shot.vision_analysis,
            "rejection_reason": shot.rejection_reason,
            "generation_attempts": shot.generation_attempts,
            "continuity_warnings": shot.continuity_warnings,
        }

    def _character(self, character: Character) -> dict[str, Any]:
        return {
            "id": character.id,
            "name": character.name,
            "face": character.face,
            "hair": character.hair,
            "skin": character.skin,
            "height": character.height,
            "body": character.body,
            "clothes": character.clothes,
            "accessories": character.accessories,
            "walking_style": character.walking_style,
            "expressions": character.expressions,
            "reference_images": character.reference_images,
        }

    def _prop(self, prop: Prop) -> dict[str, Any]:
        return {
            "id": prop.id,
            "name": prop.name,
            "category": prop.category,
            "description": prop.description,
            "position": prop.position,
            "damage_state": prop.damage_state,
            "reference_images": prop.reference_images,
        }

    def _workflow(self, workflow: DirectorWorkflow) -> dict[str, Any]:
        return {
            "id": workflow.id,
            "shot_id": workflow.shot_id,
            "director_instruction": workflow.director_instruction,
            "higgsfield_prompt": workflow.higgsfield_prompt,
            "approval_status": workflow.approval_status,
            "review_reasons": workflow.review_reasons,
            "improved_gpt_prompt": workflow.improved_gpt_prompt,
            "improved_claude_prompt": workflow.improved_claude_prompt,
        }

    def _visual_memory(self, memory: VisualMemory) -> dict[str, Any]:
        return {
            "shot_id": memory.shot_id,
            "scene_id": memory.scene_id,
            "character_id": memory.character_id,
            "approved_image": memory.approved_image,
            "state": memory.state,
            "extraction_source": memory.extraction_source,
        }

    def _experiment(self, experiment: GenerationExperiment) -> dict[str, Any]:
        return {
            "shot_id": experiment.shot_id,
            "provider": experiment.provider,
            "provider_model": experiment.provider_model,
            "prompt": experiment.prompt,
            "scores": {
                "face": experiment.face_score,
                "body": experiment.body_score,
                "costume": experiment.costume_score,
                "environment": experiment.environment_score,
                "lighting": experiment.lighting_score,
                "camera": experiment.camera_score,
                "overall": experiment.overall_score,
            },
            "accepted": experiment.accepted,
            "metadata": experiment.metadata_json,
        }

    def _prompt_genome(self, genome: PromptGenome) -> dict[str, Any]:
        return {"shot_id": genome.shot_id, "prompt_hash": genome.prompt_hash, "genes": genome.genes}

    def _provider_behavior(self, behavior: ProviderBehaviorRecord) -> dict[str, Any]:
        return {
            "provider": behavior.provider,
            "provider_model": behavior.provider_model,
            "provider_version": behavior.provider_version,
            "reference_strength": behavior.reference_strength,
            "scores": {
                "face": behavior.face_score,
                "camera": behavior.camera_score,
                "lighting": behavior.lighting_score,
                "environment": behavior.environment_score,
                "costume": behavior.costume_score,
            },
            "learned_observations": behavior.learned_observations,
        }

    def _human_review(self, review: HumanReview) -> dict[str, Any]:
        return {
            "shot_id": review.shot_id,
            "ratings": {
                "face_consistency": review.face_consistency,
                "costume": review.costume,
                "environment": review.environment,
                "lighting": review.lighting,
                "cinematography": review.cinematography,
                "motion": review.motion,
                "overall_quality": review.overall_quality,
            },
            "notes": review.notes,
            "calibration_delta": review.calibration_delta,
        }

    def _critic_review(self, review: CriticReview) -> dict[str, Any]:
        return {
            "shot_id": review.shot_id,
            "critic_role": review.critic_role,
            "failure_categories": [
                value
                for value in [
                    review.face_drift,
                    review.hair_drift,
                    review.costume_drift,
                    review.lighting_drift,
                    review.environment_drift,
                    review.camera_drift,
                ]
                if value
            ],
            "differences": review.differences,
            "suggested_corrections": review.suggested_corrections,
            "corrected_prompt": review.corrected_prompt,
            "overall_score": review.overall_score,
        }
