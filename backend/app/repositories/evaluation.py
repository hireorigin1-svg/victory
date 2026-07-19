from sqlalchemy import select

from app.models.evaluation import (
    BenchmarkProject,
    BenchmarkRun,
    BenchmarkShotScore,
    GenerationDatasetRecord,
    HumanReview,
    ProviderCapability,
)
from app.repositories.base import SQLAlchemyRepository


class BenchmarkProjectRepository(SQLAlchemyRepository[BenchmarkProject]):
    model = BenchmarkProject

    def get_by_name(self, name: str) -> BenchmarkProject | None:
        return self.db.scalars(select(BenchmarkProject).where(BenchmarkProject.name == name)).first()


class BenchmarkRunRepository(SQLAlchemyRepository[BenchmarkRun]):
    model = BenchmarkRun

    def list_for_benchmark(self, benchmark_id: str) -> list[BenchmarkRun]:
        return list(
            self.db.scalars(
                select(BenchmarkRun).where(BenchmarkRun.benchmark_id == benchmark_id).order_by(BenchmarkRun.created_at.desc())
            ).all()
        )


class BenchmarkShotScoreRepository(SQLAlchemyRepository[BenchmarkShotScore]):
    model = BenchmarkShotScore

    def list_for_run(self, run_id: str) -> list[BenchmarkShotScore]:
        return list(
            self.db.scalars(
                select(BenchmarkShotScore).where(BenchmarkShotScore.benchmark_run_id == run_id)
            ).all()
        )


class HumanReviewRepository(SQLAlchemyRepository[HumanReview]):
    model = HumanReview

    def list_for_shot(self, shot_id: str) -> list[HumanReview]:
        return list(self.db.scalars(select(HumanReview).where(HumanReview.shot_id == shot_id)).all())


class ProviderCapabilityRepository(SQLAlchemyRepository[ProviderCapability]):
    model = ProviderCapability

    def list_for_provider(self, provider: str) -> list[ProviderCapability]:
        return list(self.db.scalars(select(ProviderCapability).where(ProviderCapability.provider == provider)).all())


class GenerationDatasetRepository(SQLAlchemyRepository[GenerationDatasetRecord]):
    model = GenerationDatasetRecord
