from statistics import mean

from app.repositories.generation_experiments import GenerationExperimentRepository


class DirectorMemory:
    def __init__(self, experiments: GenerationExperimentRepository) -> None:
        self.experiments = experiments

    def summarize(self) -> dict:
        rows = self.experiments.list(limit=1000)
        accepted = [row for row in rows if row.accepted]
        rejected = [row for row in rows if not row.accepted]
        by_provider: dict[str, list[float]] = {}
        for row in rows:
            if row.overall_score is None:
                continue
            by_provider.setdefault(row.provider, []).append(row.overall_score)
        return {
            "total_experiments": len(rows),
            "accepted": len(accepted),
            "rejected": len(rejected),
            "acceptance_rate": round((len(accepted) / len(rows)) * 100, 2) if rows else 0,
            "provider_average_scores": {
                provider: round(mean(scores), 2) for provider, scores in by_provider.items()
            },
        }
