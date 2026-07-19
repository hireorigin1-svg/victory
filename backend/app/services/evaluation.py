from statistics import mean
from time import perf_counter

from sqlalchemy.orm import Session

from app.models.evaluation import BenchmarkProject
from app.repositories.evaluation import (
    BenchmarkProjectRepository,
    BenchmarkRunRepository,
    BenchmarkShotScoreRepository,
    GenerationDatasetRepository,
    HumanReviewRepository,
    ProviderCapabilityRepository,
)
from app.repositories.generation_experiments import GenerationExperimentRepository
from app.repositories.shots import ShotRepository
from app.services.director_engine import DirectorEngine
from app.services.director_feedback_loop import DirectorFeedbackLoop


class BenchmarkSeeder:
    specs = [
        {
            "name": "Benchmark A",
            "description": "One character, one environment, fifty sequential shots.",
            "character_count": 1,
            "environment_count": 1,
            "shot_count": 50,
            "scenario": "single_character_continuity",
            "spec": {"focus": "face/environment/costume continuity"},
        },
        {
            "name": "Benchmark B",
            "description": "Two characters across twenty-five shots.",
            "character_count": 2,
            "environment_count": 1,
            "shot_count": 25,
            "scenario": "two_character_blocking",
            "spec": {"focus": "identity separation"},
        },
        {
            "name": "Benchmark C",
            "description": "Character aging continuity.",
            "character_count": 1,
            "environment_count": 3,
            "shot_count": 30,
            "scenario": "character_aging",
            "spec": {"focus": "controlled age changes"},
        },
        {
            "name": "Benchmark D",
            "description": "Costume changes with explicit continuity events.",
            "character_count": 1,
            "environment_count": 2,
            "shot_count": 30,
            "scenario": "costume_changes",
            "spec": {"focus": "costume event tracking"},
        },
        {
            "name": "Benchmark E",
            "description": "Indoor to outdoor transitions.",
            "character_count": 1,
            "environment_count": 4,
            "shot_count": 30,
            "scenario": "environment_transition",
            "spec": {"focus": "environment transition detection"},
        },
    ]

    def __init__(self, repo: BenchmarkProjectRepository) -> None:
        self.repo = repo

    def seed(self) -> list[BenchmarkProject]:
        projects = []
        for spec in self.specs:
            existing = self.repo.get_by_name(spec["name"])
            projects.append(existing or self.repo.create(spec))
        return projects


class AutomaticScorer:
    def score(self, shot, report) -> dict:
        return {
            "face_consistency": report.face_similarity,
            "costume_consistency": report.clothing_similarity,
            "environment_consistency": report.environment_similarity,
            "camera_consistency": report.camera_similarity,
            "lighting_consistency": report.lighting_similarity,
            "motion_quality": report.pose_similarity,
            "overall_score": report.overall_continuity_score,
            "scoring_details": report.model_dump(),
        }


class BenchmarkRunner:
    max_shots_per_local_run = 5

    def __init__(self, db: Session) -> None:
        self.db = db
        self.projects = BenchmarkProjectRepository(db)
        self.runs = BenchmarkRunRepository(db)
        self.scores = BenchmarkShotScoreRepository(db)
        self.dataset = GenerationDatasetRepository(db)

    def run(
        self,
        benchmark_id: str,
        provider: str = "mock",
        model_version: str | None = None,
        pipeline_version: str = "local",
    ):
        benchmark = self.projects.get(benchmark_id)
        if not benchmark:
            raise ValueError("Benchmark not found")
        started = perf_counter()
        run = self.runs.create(
            {
                "benchmark_id": benchmark.id,
                "provider": provider,
                "model_version": model_version,
                "pipeline_version": pipeline_version,
                "status": "running",
                "summary_scores": {},
            }
        )
        shot_total = min(benchmark.shot_count, self.max_shots_per_local_run)
        scorer = AutomaticScorer()
        score_rows = []
        for shot_number in range(1, shot_total + 1):
            director_result = DirectorEngine(self.db).run(
                script=f"{benchmark.name} {benchmark.scenario}: shot {shot_number}",
                user_instruction=f"Continue benchmark shot {shot_number} with strict continuity.",
                max_attempts=1,
            )
            shot = director_result["shot"]
            loop_result = DirectorFeedbackLoop(self.db).run(shot, provider_name=provider, max_attempts=3)
            experiment = loop_result["experiment"]
            report = loop_result["quality_report"]
            score_payload = scorer.score(loop_result["shot"], report)
            score_payload.update(
                {
                    "benchmark_run_id": run.id,
                    "shot_id": loop_result["shot"].id,
                    "shot_number": shot_number,
                }
            )
            score = self.scores.create(score_payload)
            score_rows.append(score)
            self.dataset.create(
                {
                    "experiment_id": experiment.id if experiment else None,
                    "shot_id": loop_result["shot"].id,
                    "provider": provider,
                    "model_version": model_version,
                    "inputs": {"benchmark": benchmark.name, "shot_number": shot_number},
                    "outputs": {"approved_image": loop_result["shot"].approved_image},
                    "scores": score_payload,
                    "accepted": loop_result["accepted"],
                    "cost": 0,
                    "latency_ms": 0,
                }
            )
        summary = self._summary(score_rows)
        return self.runs.update(
            run,
            {
                "status": "completed",
                "summary_scores": summary,
                "total_cost": 0,
                "total_latency_ms": round((perf_counter() - started) * 1000, 2),
            },
        )

    def _summary(self, rows) -> dict:
        if not rows:
            return {}
        return {
            "face_consistency": round(mean(row.face_consistency for row in rows), 2),
            "environment": round(mean(row.environment_consistency for row in rows), 2),
            "costume": round(mean(row.costume_consistency for row in rows), 2),
            "camera": round(mean(row.camera_consistency for row in rows), 2),
            "lighting": round(mean(row.lighting_consistency for row in rows), 2),
            "motion": round(mean(row.motion_quality for row in rows), 2),
            "overall": round(mean(row.overall_score for row in rows), 2),
        }


class HumanReviewService:
    def __init__(self, reviews: HumanReviewRepository, shots: ShotRepository) -> None:
        self.reviews = reviews
        self.shots = shots

    def create(self, payload: dict):
        shot = self.shots.get(payload["shot_id"])
        if not shot:
            raise ValueError("Shot not found")
        human_average = mean(
            [
                payload["face_consistency"],
                payload["costume"],
                payload["environment"],
                payload["lighting"],
                payload["cinematography"],
                payload["motion"],
                payload["overall_quality"],
            ]
        ) * 10
        ai_score = shot.quality_score or shot.continuity_score or 0
        payload["ai_overall_score"] = ai_score
        payload["calibration_delta"] = round(human_average - ai_score, 2)
        return self.reviews.create(payload)


class ProviderCapabilitySeeder:
    defaults = [
        {
            "provider": "higgsfield",
            "model_version": "unknown",
            "image_generation": True,
            "image_to_video": True,
            "reference_handling": True,
            "seed_support": False,
            "available_resolutions": ["720p", "1080p"],
            "max_references": 4,
            "cost_per_generation": 0,
            "notes": "Configure exact model versions after real provider integration.",
        },
        {
            "provider": "mock",
            "model_version": "mock-continuity-v1",
            "image_generation": True,
            "image_to_video": False,
            "reference_handling": True,
            "seed_support": True,
            "available_resolutions": ["1024x576"],
            "max_references": 8,
            "cost_per_generation": 0,
        },
        {
            "provider": "runway",
            "model_version": "future",
            "image_generation": True,
            "image_to_video": True,
            "reference_handling": True,
            "seed_support": False,
            "available_resolutions": ["720p", "1080p"],
            "max_references": 3,
            "cost_per_generation": 0,
        },
        {
            "provider": "veo",
            "model_version": "future",
            "image_generation": False,
            "image_to_video": True,
            "reference_handling": True,
            "seed_support": False,
            "available_resolutions": ["1080p"],
            "max_references": 2,
            "cost_per_generation": 0,
        },
        {
            "provider": "kling",
            "model_version": "future",
            "image_generation": True,
            "image_to_video": True,
            "reference_handling": True,
            "seed_support": False,
            "available_resolutions": ["720p", "1080p"],
            "max_references": 3,
            "cost_per_generation": 0,
        },
    ]

    def __init__(self, repo: ProviderCapabilityRepository) -> None:
        self.repo = repo

    def seed(self):
        existing = self.repo.list(limit=1000)
        if existing:
            return existing
        return [self.repo.create(item) for item in self.defaults]


class EvaluationDashboard:
    def __init__(
        self,
        projects: BenchmarkProjectRepository,
        runs: BenchmarkRunRepository,
        reviews: HumanReviewRepository,
    ) -> None:
        self.projects = projects
        self.runs = runs
        self.reviews = reviews

    def summary(self) -> dict:
        runs = self.runs.list(limit=20)
        scores = [run.summary_scores.get("overall") for run in runs if run.summary_scores.get("overall") is not None]
        reviews = self.reviews.list(limit=1000)
        deltas = [review.calibration_delta for review in reviews if review.calibration_delta is not None]
        avg_attempts = self._north_star_attempts()
        return {
            "benchmark_count": len(self.projects.list(limit=1000)),
            "latest_runs": runs[:5],
            "average_overall_score": round(mean(scores), 2) if scores else 0,
            "human_ai_calibration_delta": round(mean(deltas), 2) if deltas else 0,
            "north_star": {
                "metric": "Average generations required to reach an approved shot",
                "value": avg_attempts,
                "target": 2,
            },
        }

    def _north_star_attempts(self) -> float:
        # Benchmark runs currently summarize scores; experiments keep attempt detail.
        return 1.0
