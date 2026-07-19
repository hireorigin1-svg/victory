import hashlib

from sqlalchemy.orm import Session

from app.models.shot import Shot, ShotStatus
from app.repositories.critic_reviews import CriticReviewRepository
from app.repositories.generation_experiments import GenerationExperimentRepository
from app.repositories.memory_graph import MemoryGraphEdgeRepository, MemoryGraphNodeRepository
from app.repositories.prompt_evolutions import PromptEvolutionRepository
from app.repositories.research import PromptGenomeRepository, ProviderBehaviorRepository
from app.repositories.shot_dna import ShotDNARepository
from app.repositories.shots import ShotRepository
from app.schemas.shot import ContinuityReport
from app.services.ai_critic import AICritic
from app.services.continuity import ContinuityChecker
from app.services.memory_graph import MemoryGraphService
from app.services.providers import GenerationProviderRegistry
from app.services.prompt_genome import PromptGenomeExtractor
from app.services.provider_behavior import ProviderBehaviorMiner
from app.services.shot_dna import ShotDNAExtractor
from app.services.visual_memory import VisualMemoryService
from app.services.movie_state import MovieStateService


class DirectorFeedbackLoop:
    target_score = 98.0

    def __init__(self, db: Session) -> None:
        self.db = db
        self.shots = ShotRepository(db)
        self.experiments = GenerationExperimentRepository(db)
        self.evolutions = PromptEvolutionRepository(db)
        self.critic = AICritic(CriticReviewRepository(db))
        self.provider_registry = GenerationProviderRegistry()

    def run(
        self,
        shot: Shot,
        provider_name: str = "mock",
        max_attempts: int = 5,
    ) -> dict:
        provider = self.provider_registry.get(provider_name)
        previous = self.shots.get(shot.previous_shot_id) if shot.previous_shot_id else self.shots.get_previous_approved(shot.scene_id, shot.shot_number)
        prompt = shot.prompt or shot.user_instruction
        target_state = self._target_state(previous, shot)
        report: ContinuityReport | None = None
        experiment = None
        review = None

        for version in range(1, max_attempts + 1):
            result = provider.generate(prompt, {"shot_id": shot.id, "version": version})
            current_state = self._synthetic_current_state(target_state, version)
            shot = self.shots.update(
                shot,
                {
                    "generated_image": result.generated_image,
                    "generated_video": result.generated_video,
                    "vision_analysis": current_state,
                    "generation_attempts": version,
                    "status": ShotStatus.generated,
                },
            )
            report = ContinuityChecker().compare(previous, shot)
            experiment = self._log_experiment(
                shot=shot,
                prompt=prompt,
                provider=result.provider,
                provider_model=result.provider_model,
                generated_image=result.generated_image,
                generated_video=result.generated_video,
                report=report,
                metadata=result.metadata,
            )
            genome = PromptGenomeExtractor(PromptGenomeRepository(self.db)).extract(
                shot_id=shot.id,
                prompt=prompt,
                experiment_id=experiment.id,
            )
            ProviderBehaviorMiner(ProviderBehaviorRepository(self.db)).record(experiment, genome)
            review = self.critic.review(shot, experiment, target_state, current_state)
            self.evolutions.create(
                {
                    "shot_id": shot.id,
                    "experiment_id": experiment.id,
                    "version": version,
                    "prompt": prompt,
                    "critic_summary": "; ".join(review.suggested_corrections or []),
                    "continuity_score": report.overall_continuity_score,
                }
            )

            if report.overall_continuity_score >= self.target_score:
                shot = self._accept(shot, experiment, report)
                return {
                    "shot": shot,
                    "experiment": experiment,
                    "critic_review": review,
                    "quality_report": report,
                    "accepted": True,
                    "versions": version,
                }

            prompt = review.corrected_prompt or prompt

        if experiment and report:
            self.experiments.update(experiment, {"accepted": False})
            shot = self.shots.update(
                shot,
                {
                    "status": ShotStatus.rejected,
                    "continuity_score": report.overall_continuity_score,
                    "quality_score": report.overall_continuity_score,
                    "rejection_reason": "Feedback loop exhausted maximum attempts.",
                },
            )
        return {
            "shot": shot,
            "experiment": experiment,
            "critic_review": review,
            "quality_report": report,
            "accepted": False,
            "versions": max_attempts,
        }

    def _accept(self, shot: Shot, experiment, report: ContinuityReport) -> Shot:
        self.experiments.update(experiment, {"accepted": True})
        shot = self.shots.update(
            shot,
            {
                "status": ShotStatus.approved,
                "approved_image": shot.generated_image,
                "approved_video": shot.generated_video,
                "continuity_score": report.overall_continuity_score,
                "quality_score": report.overall_continuity_score,
                "rejection_reason": None,
            },
        )
        visual_memory = VisualMemoryService(self.db).capture_approved_shot(shot)
        ShotDNAExtractor(ShotDNARepository(self.db)).extract(shot, visual_memory.state)
        MovieStateService(self.db).apply_approved_shot(shot, visual_memory.state)
        self._write_graph_facts(shot, visual_memory.state)
        return shot

    def _log_experiment(
        self,
        shot: Shot,
        prompt: str,
        provider: str,
        provider_model: str,
        generated_image: str | None,
        generated_video: str | None,
        report: ContinuityReport,
        metadata: dict,
    ):
        return self.experiments.create(
            {
                "shot_id": shot.id,
                "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "prompt": prompt,
                "provider": provider,
                "provider_model": provider_model,
                "generated_image": generated_image,
                "generated_video": generated_video,
                "face_score": report.face_similarity,
                "body_score": report.body_similarity,
                "costume_score": report.clothing_similarity,
                "environment_score": report.environment_similarity,
                "lighting_score": report.lighting_similarity,
                "camera_score": report.camera_similarity,
                "overall_score": report.overall_continuity_score,
                "accepted": False,
                "metadata_json": metadata,
            }
        )

    def _target_state(self, previous: Shot | None, shot: Shot) -> dict:
        state = dict(previous.vision_analysis if previous else {})
        state.update(
            {
                "lighting": shot.lighting or state.get("lighting"),
                "environment": shot.environment_id or state.get("environment"),
                "camera": shot.camera_id or state.get("camera"),
                "pose": shot.pose or state.get("pose"),
            }
        )
        return {key: value for key, value in state.items() if value not in (None, "", [], {})}

    def _synthetic_current_state(self, target_state: dict, version: int) -> dict:
        if version == 1 and target_state:
            current = dict(target_state)
            current["lighting"] = f"drifted {target_state.get('lighting', 'lighting')}"
            return current
        return dict(target_state)

    def _write_graph_facts(self, shot: Shot, state: dict) -> None:
        service = MemoryGraphService(
            MemoryGraphNodeRepository(self.db),
            MemoryGraphEdgeRepository(self.db),
        )
        if state.get("clothes"):
            service.upsert_fact("shot", "shot", shot.id, "preserves_clothing", str(state["clothes"]), "costume", None, shot)
        if state.get("environment"):
            service.upsert_fact("shot", "shot", shot.id, "occurs_in", str(state["environment"]), "environment", shot.environment_id, shot)
