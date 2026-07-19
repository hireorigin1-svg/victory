from sqlalchemy.orm import Session

from app.repositories.movie_states import MovieStateRepository
from app.repositories.research import SceneSimulationRepository
from app.repositories.scenes import SceneRepository


class SceneSimulator:
    def __init__(self, db: Session, simulations: SceneSimulationRepository) -> None:
        self.db = db
        self.simulations = simulations

    def simulate(self, scene_id: str):
        scene = SceneRepository(self.db).get(scene_id)
        if not scene:
            raise ValueError("Scene not found")
        movie_state = MovieStateRepository(self.db).get_default()
        expected = dict(movie_state.state if movie_state else {})
        expected.update(
            {
                "scene_id": scene.id,
                "environment_id": scene.environment_id,
                "timeline": scene.timeline,
                "character_ids": scene.character_ids,
                "prop_ids": scene.prop_ids,
            }
        )
        conflicts = []
        if movie_state and movie_state.state.get("environment_id") and scene.environment_id:
            if movie_state.state["environment_id"] != scene.environment_id and "travels" not in scene.script.lower():
                conflicts.append("Environment changes without an explicit travel/story transition.")
        constraints = [
            "Preserve current movie state unless the script explicitly changes it.",
            "Load canonical character identity profiles before generation.",
        ]
        return self.simulations.create(
            {
                "scene_id": scene.id,
                "expected_state": expected,
                "detected_conflicts": conflicts,
                "recommended_prompt_constraints": constraints,
                "safe_to_generate": len(conflicts) == 0,
            }
        )
