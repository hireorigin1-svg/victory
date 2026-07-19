from fastapi import APIRouter

from app.api.v1 import (
    auth,
    brain,
    cameras,
    characters,
    director,
    director_workflows,
    environments,
    evaluation,
    film_bible,
    media,
    memory,
    props,
    research,
    scenes,
    shots,
    visual_intelligence,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(brain.router)
api_router.include_router(cameras.router)
api_router.include_router(characters.router)
api_router.include_router(director.router)
api_router.include_router(director_workflows.router)
api_router.include_router(environments.router)
api_router.include_router(evaluation.router)
api_router.include_router(film_bible.router)
api_router.include_router(media.router)
api_router.include_router(memory.router)
api_router.include_router(props.router)
api_router.include_router(research.router)
api_router.include_router(scenes.router)
api_router.include_router(shots.router)
api_router.include_router(visual_intelligence.router)
