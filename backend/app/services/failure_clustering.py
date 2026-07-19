from app.repositories.generation_experiments import GenerationExperimentRepository
from app.repositories.visual_intelligence import FailureClusterRepository


class FailureClusteringService:
    def __init__(self, experiments: GenerationExperimentRepository, clusters: FailureClusterRepository) -> None:
        self.experiments = experiments
        self.clusters = clusters

    def cluster(self):
        rows = [row for row in self.experiments.list(limit=1000) if not row.accepted]
        categories = {
            "face_drift": [row for row in rows if (row.face_score or 100) < 90],
            "costume_drift": [row for row in rows if (row.costume_score or 100) < 90],
            "environment_drift": [row for row in rows if (row.environment_score or 100) < 90],
            "lighting_drift": [row for row in rows if (row.lighting_score or 100) < 90],
            "camera_drift": [row for row in rows if (row.camera_score or 100) < 90],
        }
        clusters = []
        for cluster_type, items in categories.items():
            if not items:
                continue
            clusters.append(
                self.clusters.create(
                    {
                        "cluster_type": cluster_type,
                        "experiment_ids": [item.id for item in items],
                        "common_causes": [f"{cluster_type} appears in {len(items)} failed generation(s)."],
                        "recommended_actions": [f"Run Prompt Scientist on {cluster_type} and rewrite only affected AST branch."],
                    }
                )
            )
        return clusters
