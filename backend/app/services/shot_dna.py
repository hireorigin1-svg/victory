from app.models.shot import Shot
from app.repositories.shot_dna import ShotDNARepository


class ShotDNAExtractor:
    def __init__(self, repo: ShotDNARepository) -> None:
        self.repo = repo

    def extract(self, shot: Shot, visual_state: dict | None = None, character_id: str | None = None):
        state = visual_state or shot.vision_analysis or {}
        dna = {
            "face": {
                "geometry": state.get("face_geometry") or state.get("face"),
                "eyes": state.get("eyes"),
                "nose": state.get("nose"),
                "jaw": state.get("jaw"),
            },
            "costume": {
                "primary_color": state.get("costume_primary_color"),
                "fabric": state.get("fabric"),
                "accessories": state.get("accessories") or state.get("props"),
                "clothing": state.get("clothes"),
            },
            "lighting": {
                "temperature": state.get("lighting_temperature") or 5600,
                "direction": state.get("lighting_direction") or "unknown",
                "contrast": state.get("lighting_contrast") or state.get("lighting"),
            },
            "camera": {
                "lens": state.get("lens") or state.get("camera"),
                "height": state.get("camera_height"),
                "distance": state.get("camera_distance"),
            },
            "environment": state.get("environment"),
            "pose": state.get("pose"),
            "props": state.get("props", []),
        }
        existing = self.repo.get_for_shot(shot.id)
        payload = {
            "shot_id": shot.id,
            "scene_id": shot.scene_id,
            "character_id": character_id,
            "source_image": shot.approved_image or shot.generated_image,
            "dna": dna,
            "extractor": "gpt-vision-ready",
        }
        if existing:
            return self.repo.update(existing, payload)
        return self.repo.create(payload)
