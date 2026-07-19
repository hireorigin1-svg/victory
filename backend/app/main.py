from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import Base, engine
from app import models  # noqa: F401
from app.db.session import SessionLocal
from app.models.user import UserRole
from app.repositories.users import UserRepository
from app.services.auth import AuthService


def create_app(seed_data: bool = True) -> FastAPI:
    settings = get_settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def create_tables() -> None:
        Base.metadata.create_all(bind=engine)
        if seed_data:
            seed_director()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    app.include_router(api_router)
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
    return app


app = create_app()


def seed_director() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        users = UserRepository(db)
        if users.get_by_email(settings.seed_director_email):
            return
        AuthService(users).register(
            email=settings.seed_director_email,
            name="Victory Director",
            password=settings.seed_director_password,
            role=UserRole.director,
        )
    finally:
        db.close()
