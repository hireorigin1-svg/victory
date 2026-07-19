from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.evaluation import (
    BenchmarkProjectRepository,
    BenchmarkRunRepository,
    BenchmarkShotScoreRepository,
    HumanReviewRepository,
    ProviderCapabilityRepository,
    GenerationDatasetRepository,
)
from app.repositories.generation_experiments import GenerationExperimentRepository
from app.repositories.research import PromptGenomeRepository, ProviderBehaviorRepository
from app.repositories.shots import ShotRepository
from app.schemas.evaluation import (
    BenchmarkProjectRead,
    BenchmarkRunRead,
    BenchmarkRunRequest,
    BenchmarkShotScoreRead,
    EvaluationDashboardRead,
    AutonomousBatchRead,
    BenchmarkGateRead,
    DebateRead,
    DebateRequest,
    HumanReviewCreate,
    HumanReviewRead,
    ExperimentPlanRead,
    GeneLearningRead,
    ProviderDNARead,
    ResearchReportRead,
    SymbolicPromptRead,
    SymbolicPromptRequest,
    ProviderCapabilityRead,
)
from app.services.evaluation import (
    BenchmarkRunner,
    BenchmarkSeeder,
    EvaluationDashboard,
    HumanReviewService,
    ProviderCapabilitySeeder,
)
from app.services.research_ops import (
    AutonomousExperimentEngine,
    BenchmarkGate,
    ExperimentPlanGenerator,
    MultiAgentDebate,
    PromptGeneLearner,
    ProviderDNALearner,
    ResearchReportGenerator,
    SymbolicPromptLanguage,
)

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/benchmarks/seed", response_model=list[BenchmarkProjectRead])
def seed_benchmarks(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    return BenchmarkSeeder(BenchmarkProjectRepository(db)).seed()


@router.get("/benchmarks", response_model=list[BenchmarkProjectRead])
def list_benchmarks(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return BenchmarkProjectRepository(db).list(limit=1000)


@router.post("/benchmark-runs", response_model=BenchmarkRunRead)
def run_benchmark(
    payload: BenchmarkRunRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    try:
        return BenchmarkRunner(db).run(
            benchmark_id=payload.benchmark_id,
            provider=payload.provider,
            model_version=payload.model_version,
            pipeline_version=payload.pipeline_version,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/benchmark-runs", response_model=list[BenchmarkRunRead])
def list_benchmark_runs(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return BenchmarkRunRepository(db).list(limit=100)


@router.get("/benchmark-runs/{run_id}/scores", response_model=list[BenchmarkShotScoreRead])
def list_run_scores(
    run_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return BenchmarkShotScoreRepository(db).list_for_run(run_id)


@router.post("/human-reviews", response_model=HumanReviewRead)
def create_human_review(
    payload: HumanReviewCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director, UserRole.editor)),
):
    try:
        return HumanReviewService(HumanReviewRepository(db), ShotRepository(db)).create(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/human-reviews/{shot_id}", response_model=list[HumanReviewRead])
def list_human_reviews(
    shot_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return HumanReviewRepository(db).list_for_shot(shot_id)


@router.post("/providers/seed", response_model=list[ProviderCapabilityRead])
def seed_provider_capabilities(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    return ProviderCapabilitySeeder(ProviderCapabilityRepository(db)).seed()


@router.get("/providers", response_model=list[ProviderCapabilityRead])
def list_provider_capabilities(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ProviderCapabilityRepository(db).list(limit=1000)


@router.get("/dashboard", response_model=EvaluationDashboardRead)
def evaluation_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return EvaluationDashboard(
        BenchmarkProjectRepository(db),
        BenchmarkRunRepository(db),
        HumanReviewRepository(db),
    ).summary()


@router.get("/research/experiment-plan", response_model=ExperimentPlanRead)
def experiment_plan(
    variants_per_factor: int = 3,
    _: User = Depends(get_current_user),
):
    return ExperimentPlanGenerator().plan(variants_per_factor=variants_per_factor)


@router.post("/research/autonomous-batch", response_model=AutonomousBatchRead)
def run_autonomous_batch(
    provider: str = "mock",
    max_benchmarks: int = 2,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.director)),
):
    return AutonomousExperimentEngine(db).run_nightly_batch(
        provider=provider,
        max_benchmarks=max_benchmarks,
    )


@router.get("/research/gene-learning", response_model=GeneLearningRead)
def gene_learning(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return PromptGeneLearner(
        PromptGenomeRepository(db),
        GenerationExperimentRepository(db),
    ).learn()


@router.get("/research/provider-dna", response_model=ProviderDNARead)
def provider_dna(
    provider: str = "higgsfield",
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ProviderDNALearner(ProviderBehaviorRepository(db)).learn(provider)


@router.get("/research/monthly-report", response_model=ResearchReportRead)
def monthly_report(
    month_label: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ResearchReportGenerator(
        BenchmarkRunRepository(db),
        GenerationExperimentRepository(db),
        GenerationDatasetRepository(db),
        PromptGenomeRepository(db),
    ).monthly_report(month_label=month_label)


@router.get("/research/benchmark-gate", response_model=BenchmarkGateRead)
def benchmark_gate(
    baseline_run_id: str,
    candidate_run_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return BenchmarkGate(BenchmarkRunRepository(db)).evaluate_change(
            baseline_run_id=baseline_run_id,
            candidate_run_id=candidate_run_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/research/debate", response_model=DebateRead)
def debate_prompt(
    payload: DebateRequest,
    _: User = Depends(get_current_user),
):
    return MultiAgentDebate().debate_prompt(payload.prompt, payload.context)


@router.post("/research/symbolic-prompt", response_model=SymbolicPromptRead)
def symbolic_prompt(
    payload: SymbolicPromptRequest,
    _: User = Depends(get_current_user),
):
    return SymbolicPromptLanguage().compile_symbols(payload.components)
