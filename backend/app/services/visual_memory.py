from sqlalchemy.orm import Session

from app.models.shot import Shot
from app.repositories.visual_memories import VisualMemoryRepository
from app.services.vision import VisionAnalyzer


class VisualMemoryService:
    def __init__(self, db: Session) -> None:
        self.repo = VisualMemoryRepository(db)
        self.analyzer = VisionAnalyzer()

    def capture_approved_shot(self, shot: Shot, character_id: str | None = None):
        analysis = self.analyzer.analyze(shot)
        existing = self.repo.get_for_shot(shot.id)
        payload = {
            "shot_id": shot.id,
            "scene_id": shot.scene_id,
            "character_id": character_id,
            "approved_image": shot.approved_image or shot.generated_image,
            "state": analysis,
            "extraction_source": "gpt-vision-ready",
        }
        if existing:
            return self.repo.update(existing, payload)
        return self.repo.create(payload)
