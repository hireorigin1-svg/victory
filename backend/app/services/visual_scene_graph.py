from app.models.shot import Shot
from app.repositories.visual_intelligence import VisualSceneGraphRepository


class VisualSceneGraphExtractor:
    def __init__(self, repo: VisualSceneGraphRepository) -> None:
        self.repo = repo

    def extract(self, shot: Shot):
        memory = shot.vision_analysis or {}
        entities = [
            {"id": "character_1", "type": "character", "name": memory.get("character", "subject")},
            {"id": "environment_1", "type": "environment", "name": memory.get("environment") or shot.environment_id},
        ]
        if memory.get("props"):
            for index, prop in enumerate(memory["props"]):
                entities.append({"id": f"prop_{index + 1}", "type": "prop", "name": prop})
        relations = [
            {"subject": "character_1", "predicate": "located_in", "object": "environment_1"},
        ]
        attributes = {
            "pose": memory.get("pose") or shot.pose,
            "lighting": memory.get("lighting") or shot.lighting,
            "camera": memory.get("camera") or shot.camera_id,
            "lens": memory.get("lens"),
            "dust_density": memory.get("dust_density"),
            "smile_intensity": memory.get("smile_intensity"),
        }
        return self.repo.create(
            {
                "shot_id": shot.id,
                "source_image": shot.approved_image or shot.generated_image,
                "entities": entities,
                "relations": relations,
                "attributes": attributes,
                "extractor": "gpt-vision-ready",
            }
        )
