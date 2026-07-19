from difflib import SequenceMatcher

from app.models.shot import Shot, ShotStatus
from app.schemas.shot import ContinuityReport


class ContinuityChecker:
    threshold = 90.0

    def compare(self, previous: Shot | None, current: Shot) -> ContinuityReport:
        if not previous:
            return ContinuityReport(
                face_similarity=100,
                hair_similarity=100,
                body_similarity=100,
                clothing_similarity=100,
                environment_similarity=100,
                lighting_similarity=100,
                pose_similarity=100,
                props_similarity=100,
                camera_similarity=100,
                overall_continuity_score=100,
                decision=ShotStatus.compiled,
                notes=["No previous approved shot; continuity baseline starts here."],
            )

        previous_memory = previous.vision_analysis or {}
        current_memory = current.vision_analysis or {}
        scores = {
            "face_similarity": self._score(previous_memory.get("face"), current_memory.get("face")),
            "hair_similarity": self._score(previous_memory.get("hair"), current_memory.get("hair")),
            "body_similarity": self._score(previous_memory.get("body"), current_memory.get("body")),
            "clothing_similarity": self._score(previous_memory.get("clothes"), current_memory.get("clothes")),
            "environment_similarity": self._score(
                previous_memory.get("environment") or previous.environment_id,
                current_memory.get("environment") or current.environment_id,
            ),
            "lighting_similarity": self._score(previous.lighting, current.lighting),
            "pose_similarity": self._score(previous.pose, current.pose),
            "props_similarity": self._score(previous_memory.get("props"), current_memory.get("props")),
            "camera_similarity": self._score(previous.camera_id, current.camera_id),
        }
        overall = round(sum(scores.values()) / len(scores), 2)
        decision = ShotStatus.approved if overall >= self.threshold else ShotStatus.rejected
        notes = []
        if decision == ShotStatus.rejected:
            notes.append("Continuity score is below 90%; regenerate before approval.")
        else:
            notes.append("Continuity score is approval-ready.")

        return ContinuityReport(
            **scores,
            overall_continuity_score=overall,
            decision=decision,
            notes=notes,
        )

    def _score(self, left: object, right: object) -> float:
        if left in (None, "", []) and right in (None, "", []):
            return 100.0
        if left in (None, "", []) or right in (None, "", []):
            return 70.0
        return round(SequenceMatcher(None, str(left), str(right)).ratio() * 100, 2)
