from app.models.shot import Shot
from app.repositories.generation_experiments import GenerationExperimentRepository
from app.repositories.research import ABTestGroupRepository
from app.services.director_feedback_loop import DirectorFeedbackLoop


class ABTestingService:
    def __init__(self, db, groups: ABTestGroupRepository) -> None:
        self.db = db
        self.groups = groups

    def run(self, shot: Shot, provider: str = "mock", variants: list[dict] | None = None):
        variants = variants or self._default_variants(shot.prompt or shot.user_instruction)
        results = []
        loop = DirectorFeedbackLoop(self.db)
        original_prompt = shot.prompt
        for variant in variants:
            shot.prompt = variant["prompt"]
            result = loop.run(shot, provider_name=provider, max_attempts=2)
            results.append(
                {
                    "variant": variant["name"],
                    "prompt": variant["prompt"],
                    "experiment_id": result["experiment"].id if result["experiment"] else None,
                    "score": result["quality_report"].overall_continuity_score if result["quality_report"] else 0,
                    "accepted": result["accepted"],
                }
            )
        shot.prompt = original_prompt
        winner = max(results, key=lambda item: item["score"]) if results else None
        return self.groups.create(
            {
                "shot_id": shot.id,
                "provider": provider,
                "variants": results,
                "winning_experiment_id": winner["experiment_id"] if winner else None,
                "winning_variant": winner["variant"] if winner else None,
                "winner_score": winner["score"] if winner else None,
            }
        )

    def _default_variants(self, prompt: str) -> list[dict]:
        return [
            {"name": "A", "prompt": prompt},
            {"name": "B", "prompt": f"{prompt}\nUse stricter reference fidelity and preserve canonical identity."},
        ]
