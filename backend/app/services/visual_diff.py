from app.models.shot import Shot
from app.repositories.visual_intelligence import VisualDiffRepository


class VisualDiffEngine:
    fields = ["face", "hair", "clothes", "environment", "camera", "lighting", "pose", "props"]

    def __init__(self, repo: VisualDiffRepository) -> None:
        self.repo = repo

    def compare(self, baseline: Shot, candidate: Shot):
        left = baseline.vision_analysis or {}
        right = candidate.vision_analysis or {}
        changes = []
        corrections = []
        for field in self.fields:
            expected = left.get(field) or self._fallback(baseline, field)
            actual = right.get(field) or self._fallback(candidate, field)
            if expected and actual and expected != actual:
                changes.append({"field": field, "expected": expected, "actual": actual})
                corrections.append(f"Restore {field} to {expected}.")
        score = max(0, 100 - len(changes) * 12.5)
        return self.repo.create(
            {
                "baseline_shot_id": baseline.id,
                "candidate_shot_id": candidate.id,
                "changes": changes,
                "corrections": corrections,
                "overall_delta_score": score,
            }
        )

    def _fallback(self, shot: Shot, field: str):
        mapping = {
            "camera": shot.camera_id,
            "environment": shot.environment_id,
            "lighting": shot.lighting,
            "pose": shot.pose,
        }
        return mapping.get(field)
