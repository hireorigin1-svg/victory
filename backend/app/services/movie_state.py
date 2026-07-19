from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.movie_state import MovieState
from app.models.shot import Shot
from app.repositories.movie_states import MovieStateRepository


class MovieStateService:
    def __init__(self, db: Session) -> None:
        self.repo = MovieStateRepository(db)

    def get_or_create(self) -> MovieState:
        state = self.repo.get_default()
        if state:
            return state
        return self.repo.create(
            {
                "project_name": "Default Project",
                "current_scene_id": None,
                "current_shot_id": None,
                "state": {},
                "history": [],
            }
        )

    def apply_approved_shot(self, shot: Shot, visual_state: dict) -> MovieState:
        movie_state = self.get_or_create()
        next_state = dict(movie_state.state or {})
        next_state.update(
            {
                "scene_id": shot.scene_id,
                "shot_id": shot.id,
                "lighting": shot.lighting,
                "emotion": shot.emotion,
                "pose": shot.pose,
                "environment_id": shot.environment_id,
                "camera_id": shot.camera_id,
                "visual_state": visual_state,
            }
        )
        history = list(movie_state.history or [])
        history.append(
            {
                "changed_at": datetime.now(timezone.utc).isoformat(),
                "shot_id": shot.id,
                "state": next_state,
            }
        )
        return self.repo.update(
            movie_state,
            {
                "current_scene_id": shot.scene_id,
                "current_shot_id": shot.id,
                "state": next_state,
                "history": history,
            },
        )
