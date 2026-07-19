from statistics import mean

from app.models.generation_experiment import GenerationExperiment
from app.models.research import PromptGenome
from app.repositories.research import ProviderBehaviorRepository


class ProviderBehaviorMiner:
    def __init__(self, repo: ProviderBehaviorRepository) -> None:
        self.repo = repo

    def record(self, experiment: GenerationExperiment, genome: PromptGenome):
        observations = self._observations(experiment, genome)
        return self.repo.create(
            {
                "provider": experiment.provider,
                "provider_model": experiment.provider_model,
                "provider_version": experiment.metadata_json.get("provider_version"),
                "prompt_genome_id": genome.id,
                "experiment_id": experiment.id,
                "reference_strength": experiment.metadata_json.get("reference_strength", 1.0),
                "face_score": experiment.face_score,
                "camera_score": experiment.camera_score,
                "lighting_score": experiment.lighting_score,
                "environment_score": experiment.environment_score,
                "costume_score": experiment.costume_score,
                "learned_observations": observations,
            }
        )

    def summarize(self, provider: str = "higgsfield") -> dict:
        rows = self.repo.list_for_provider(provider)
        if not rows:
            rows = self.repo.list(limit=1000)
        scored = [row for row in rows if row.face_score is not None]
        return {
            "provider": provider,
            "records": len(rows),
            "average_face_score": round(mean([row.face_score for row in scored]), 2) if scored else 0,
            "learned_rules": self._learned_rules(rows),
        }

    def _observations(self, experiment: GenerationExperiment, genome: PromptGenome) -> list[str]:
        observations = []
        genes = genome.genes or {}
        if "85mm" in genes.get("lens", []) and (experiment.face_score or 100) < 95:
            observations.append("85mm lens correlated with lower face consistency in this sample.")
        if "golden" in genes.get("adjectives", []) and (experiment.costume_score or 100) < 95:
            observations.append("Golden adjective correlated with costume drift in this sample.")
        return observations

    def _learned_rules(self, rows) -> list[str]:
        rules = []
        for row in rows:
            rules.extend(row.learned_observations or [])
        return sorted(set(rules))
