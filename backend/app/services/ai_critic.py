from app.models.generation_experiment import GenerationExperiment
from app.models.shot import Shot
from app.repositories.critic_reviews import CriticReviewRepository


class AICritic:
    def __init__(self, repo: CriticReviewRepository) -> None:
        self.repo = repo

    def review(
        self,
        shot: Shot,
        experiment: GenerationExperiment,
        target_state: dict,
        current_state: dict,
    ):
        differences = []
        corrections = []
        drift_fields = {}
        for field in ["face", "hair", "clothes", "lighting", "environment", "camera"]:
            expected = target_state.get(field)
            actual = current_state.get(field)
            if expected and actual and expected != actual:
                differences.append({"field": field, "expected": expected, "actual": actual})
                corrections.append(f"Restore {field} to {expected}.")
                drift_fields[f"{'costume' if field == 'clothes' else field}_drift"] = (
                    f"Expected {expected}; observed {actual}."
                )
            else:
                drift_fields[f"{'costume' if field == 'clothes' else field}_drift"] = "No material drift detected."

        corrected_prompt = shot.prompt or experiment.prompt
        if corrections:
            corrected_prompt = f"{corrected_prompt}\nContinuity corrections: {' '.join(corrections)}"

        return self.repo.create(
            {
                "shot_id": shot.id,
                "experiment_id": experiment.id,
                "critic_role": "Hollywood continuity supervisor",
                "face_drift": drift_fields.get("face_drift"),
                "hair_drift": drift_fields.get("hair_drift"),
                "costume_drift": drift_fields.get("costume_drift"),
                "lighting_drift": drift_fields.get("lighting_drift"),
                "environment_drift": drift_fields.get("environment_drift"),
                "camera_drift": drift_fields.get("camera_drift"),
                "differences": differences,
                "suggested_corrections": corrections,
                "corrected_prompt": corrected_prompt,
                "overall_score": experiment.overall_score,
            }
        )
