from statistics import mean

from app.repositories.generation_experiments import GenerationExperimentRepository
from app.repositories.shots import ShotRepository


class ProductionAnalytics:
    def __init__(self, shots: ShotRepository, experiments: GenerationExperimentRepository) -> None:
        self.shots = shots
        self.experiments = experiments

    def dashboard(self) -> dict:
        shots = self.shots.list(limit=1000)
        experiments = self.experiments.list(limit=1000)
        approved = [shot for shot in shots if shot.status == "approved"]
        by_provider: dict[str, list] = {}
        failures = {"face": 0, "costume": 0, "environment": 0, "lighting": 0, "camera": 0}
        for experiment in experiments:
            by_provider.setdefault(experiment.provider, []).append(experiment)
            if experiment.face_score is not None and experiment.face_score < 90:
                failures["face"] += 1
            if experiment.costume_score is not None and experiment.costume_score < 90:
                failures["costume"] += 1
            if experiment.environment_score is not None and experiment.environment_score < 90:
                failures["environment"] += 1
            if experiment.lighting_score is not None and experiment.lighting_score < 90:
                failures["lighting"] += 1
            if experiment.camera_score is not None and experiment.camera_score < 90:
                failures["camera"] += 1
        return {
            "average_generations_to_approval": round(mean([shot.generation_attempts or 1 for shot in approved]), 2) if approved else 0,
            "success_rate_by_provider": {
                provider: round((len([row for row in rows if row.accepted]) / len(rows)) * 100, 2)
                for provider, rows in by_provider.items()
            },
            "average_score_by_provider": {
                provider: round(mean([row.overall_score or 0 for row in rows]), 2)
                for provider, rows in by_provider.items()
            },
            "continuity_failures_by_category": failures,
            "best_prompt_genes": {},
            "cost_per_accepted_shot": 0,
        }
