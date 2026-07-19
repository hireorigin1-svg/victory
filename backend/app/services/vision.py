from app.models.shot import Shot


class VisionAnalyzer:
    def analyze(self, shot: Shot) -> dict:
        # Provider integrations can replace this deterministic extractor.
        return {
            "face": self._first_available(shot.vision_analysis.get("face"), shot.emotion),
            "hair": shot.vision_analysis.get("hair"),
            "clothes": shot.vision_analysis.get("clothes"),
            "camera": shot.camera_id,
            "lighting": shot.lighting,
            "emotion": shot.emotion,
            "pose": shot.pose,
            "environment": shot.environment_id,
            "props": shot.vision_analysis.get("props", []),
            "source_image": shot.approved_image or shot.generated_image,
        }

    def _first_available(self, *values: object) -> object:
        for value in values:
            if value:
                return value
        return None
