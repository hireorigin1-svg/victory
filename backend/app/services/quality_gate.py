from app.models.shot import Shot, ShotStatus
from app.repositories.shots import ShotRepository
from app.schemas.shot import ContinuityReport
from app.services.continuity import ContinuityChecker


class QualityGate:
    approval_score = 95.0
    rejection_score = 90.0
    max_attempts = 5

    def __init__(self, shot_repo: ShotRepository) -> None:
        self.shot_repo = shot_repo
        self.checker = ContinuityChecker()

    def evaluate(self, shot: Shot, previous: Shot | None, max_attempts: int = 5) -> ContinuityReport:
        attempts = min(max_attempts, self.max_attempts)
        report = self.checker.compare(previous, shot)
        generation_attempts = shot.generation_attempts or 0

        while report.overall_continuity_score < self.approval_score and generation_attempts < attempts:
            generation_attempts += 1
            self.shot_repo.update(
                shot,
                {
                    "generation_attempts": generation_attempts,
                    "status": ShotStatus.queued,
                    "rejection_reason": "Quality gate requested regeneration.",
                },
            )
            if report.overall_continuity_score < self.rejection_score:
                break
            report = self.checker.compare(previous, shot)

        decision = ShotStatus.approved if report.overall_continuity_score >= self.approval_score else ShotStatus.rejected
        self.shot_repo.update(
            shot,
            {
                "continuity_score": report.overall_continuity_score,
                "quality_score": report.overall_continuity_score,
                "generation_attempts": generation_attempts,
                "status": decision,
                "rejection_reason": None if decision == ShotStatus.approved else "; ".join(report.notes),
            },
        )
        report.decision = decision
        return report
