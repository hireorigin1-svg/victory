from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery(
    "cinemind",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


@celery_app.task(name="cinemind.generate_media")
def generate_media(shot_id: str) -> dict[str, str]:
    return {
        "shot_id": shot_id,
        "status": "queued",
        "message": "Media generation provider is ready to be connected.",
    }
