from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean

from sqlalchemy.orm import Session

from app.repositories.evaluation import (
    BenchmarkProjectRepository,
    BenchmarkRunRepository,
    GenerationDatasetRepository,
)
from app.repositories.generation_experiments import GenerationExperimentRepository
from app.repositories.research import PromptGenomeRepository, ProviderBehaviorRepository
from app.services.evaluation import BenchmarkRunner, BenchmarkSeeder


class ExperimentPlanGenerator:
    factors = [
        ("reference_count", [1, 2, 3, 4]),
        ("prompt_length", ["short", "medium", "long"]),
        ("lens", ["24mm", "35mm", "50mm", "85mm"]),
        ("lighting", ["warm backlight", "golden hour", "soft dawn", "high contrast"]),
        ("motion", ["low", "medium", "high"]),
        ("provider", ["mock", "higgsfield", "runway", "kling", "veo"]),
    ]

    def plan(self, variants_per_factor: int = 3) -> dict:
        variants = []
        for factor, values in self.factors:
            for value in values[:variants_per_factor]:
                variants.append(
                    {
                        "factor": factor,
                        "value": value,
                        "controlled_variables": [
                            other_factor for other_factor, _ in self.factors if other_factor != factor
                        ],
                        "hypothesis": f"Changing {factor} to {value} may change continuity score.",
                        "reproducibility_key": f"{factor}:{value}",
                    }
                )
        return {
            "objective": "Discover which controlled factors improve the average generations required to reach approval.",
            "variant_count": len(variants),
            "variants": variants,
        }


class AutonomousExperimentEngine:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.projects = BenchmarkProjectRepository(db)

    def run_nightly_batch(self, provider: str = "mock", max_benchmarks: int = 2) -> dict:
        BenchmarkSeeder(self.projects).seed()
        benchmarks = self.projects.list(limit=max_benchmarks)
        runs = []
        for benchmark in benchmarks:
            runs.append(
                BenchmarkRunner(self.db).run(
                    benchmark_id=benchmark.id,
                    provider=provider,
                    pipeline_version="autonomous-research",
                )
            )
        return {
            "provider": provider,
            "runs": runs,
            "summary": {
                "benchmarks_run": len(runs),
                "average_overall": round(
                    mean([run.summary_scores.get("overall", 0) for run in runs]), 2
                )
                if runs
                else 0,
            },
        }


class PromptGeneLearner:
    score_fields = {
        "face": "face_score",
        "camera": "camera_score",
        "lighting": "lighting_score",
        "environment": "environment_score",
        "costume": "costume_score",
    }

    def __init__(
        self,
        genomes: PromptGenomeRepository,
        experiments: GenerationExperimentRepository,
    ) -> None:
        self.genomes = genomes
        self.experiments = experiments

    def learn(self) -> dict:
        genomes = self.genomes.list(limit=2000)
        experiments_by_id = {experiment.id: experiment for experiment in self.experiments.list(limit=2000)}
        impacts: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

        for genome in genomes:
            experiment = experiments_by_id.get(genome.experiment_id)
            if not experiment:
                continue
            for gene_name, gene_values in (genome.genes or {}).items():
                if not gene_values:
                    continue
                for score_name, attr in self.score_fields.items():
                    score = getattr(experiment, attr, None)
                    if score is not None:
                        impacts[gene_name][score_name].append(score)

        learned = {}
        for gene_name, score_map in impacts.items():
            learned[gene_name] = {
                score_name: round(mean(values) - 95, 2)
                for score_name, values in score_map.items()
                if values
            }
        return {
            "baseline": 95,
            "interpretation": "Positive values indicate average lift over the 95% target; negative values indicate drag.",
            "gene_impacts": learned,
        }


class ProviderDNALearner:
    def __init__(self, behavior: ProviderBehaviorRepository) -> None:
        self.behavior = behavior

    def learn(self, provider: str = "higgsfield") -> dict:
        rows = self.behavior.list_for_provider(provider)
        if not rows:
            rows = self.behavior.list(limit=2000)
        scores = {
            "face": [row.face_score for row in rows if row.face_score is not None],
            "camera": [row.camera_score for row in rows if row.camera_score is not None],
            "lighting": [row.lighting_score for row in rows if row.lighting_score is not None],
            "environment": [row.environment_score for row in rows if row.environment_score is not None],
            "costume": [row.costume_score for row in rows if row.costume_score is not None],
        }
        likes = []
        dislikes = []
        for category, values in scores.items():
            if not values:
                continue
            avg = mean(values)
            if avg >= 97:
                likes.append(f"Strong {category} stability")
            elif avg < 93:
                dislikes.append(f"Weak {category} stability")
        observations = sorted(
            {
                observation
                for row in rows
                for observation in (row.learned_observations or [])
            }
        )
        return {
            "provider": provider,
            "sample_count": len(rows),
            "likes": likes,
            "dislikes": dislikes,
            "learned_observations": observations,
            "average_scores": {
                key: round(mean(values), 2) if values else 0 for key, values in scores.items()
            },
        }


class ResearchReportGenerator:
    def __init__(
        self,
        runs: BenchmarkRunRepository,
        experiments: GenerationExperimentRepository,
        datasets: GenerationDatasetRepository,
        genomes: PromptGenomeRepository,
    ) -> None:
        self.runs = runs
        self.experiments = experiments
        self.datasets = datasets
        self.genomes = genomes

    def monthly_report(self, month_label: str | None = None) -> dict:
        month_label = month_label or datetime.now(timezone.utc).strftime("%B %Y")
        runs = self.runs.list(limit=2000)
        experiments = self.experiments.list(limit=5000)
        datasets = self.datasets.list(limit=5000)
        accepted = [experiment for experiment in experiments if experiment.accepted]
        face_scores = [experiment.face_score for experiment in experiments if experiment.face_score is not None]
        overall_scores = [experiment.overall_score for experiment in experiments if experiment.overall_score is not None]
        return {
            "title": f"AI Filmmaking Research Report - {month_label}",
            "generation_count": len(experiments),
            "dataset_records": len(datasets),
            "benchmark_runs": len(runs),
            "acceptance_rate": round((len(accepted) / len(experiments)) * 100, 2) if experiments else 0,
            "average_face_score": round(mean(face_scores), 2) if face_scores else 0,
            "average_overall_score": round(mean(overall_scores), 2) if overall_scores else 0,
            "discoveries": self._discoveries(experiments),
            "north_star": "Reduce average generations required to reach an approved shot.",
        }

    def _discoveries(self, experiments) -> list[str]:
        if not experiments:
            return ["No generation data yet. Run benchmark or autonomous research batches first."]
        discoveries = []
        provider_scores: dict[str, list[float]] = defaultdict(list)
        for experiment in experiments:
            if experiment.overall_score is not None:
                provider_scores[experiment.provider].append(experiment.overall_score)
        for provider, scores in provider_scores.items():
            discoveries.append(f"{provider} average overall score: {round(mean(scores), 2)}%.")
        return discoveries


class BenchmarkGate:
    def __init__(self, runs: BenchmarkRunRepository) -> None:
        self.runs = runs

    def evaluate_change(self, baseline_run_id: str, candidate_run_id: str) -> dict:
        baseline = self.runs.get(baseline_run_id)
        candidate = self.runs.get(candidate_run_id)
        if not baseline or not candidate:
            raise ValueError("Benchmark run not found")
        baseline_score = baseline.summary_scores.get("overall", 0)
        candidate_score = candidate.summary_scores.get("overall", 0)
        delta = round(candidate_score - baseline_score, 2)
        return {
            "baseline_run_id": baseline_run_id,
            "candidate_run_id": candidate_run_id,
            "baseline_overall": baseline_score,
            "candidate_overall": candidate_score,
            "delta": delta,
            "passes_gate": delta >= 0,
            "rule": "Every code or pipeline change must preserve or improve benchmark overall score.",
        }


class MultiAgentDebate:
    agents = [
        ("Director", "story intent and performance clarity"),
        ("Cinematographer", "camera, lens, movement, and framing"),
        ("Costume Designer", "costume and accessory continuity"),
        ("Continuity Supervisor", "visual memory and Film Bible consistency"),
        ("Critic", "risk of drift and audience-visible quality"),
    ]

    def debate_prompt(self, prompt: str, context: dict | None = None) -> dict:
        context = context or {}
        votes = []
        for agent, focus in self.agents:
            risk = self._risk(prompt, agent)
            votes.append(
                {
                    "agent": agent,
                    "focus": focus,
                    "vote": "approve" if risk < 2 else "revise",
                    "risk_score": risk,
                    "recommendation": self._recommendation(agent, risk),
                }
            )
        revise_votes = len([vote for vote in votes if vote["vote"] == "revise"])
        return {
            "prompt": prompt,
            "context": context,
            "votes": votes,
            "decision": "revise" if revise_votes >= 2 else "approve",
            "final_recommendation": "Send to generation"
            if revise_votes < 2
            else "Revise only the highest-risk prompt branches before generation.",
        }

    def _risk(self, prompt: str, agent: str) -> int:
        lower = prompt.lower()
        risk = 0
        if agent == "Cinematographer" and not any(
            term in lower for term in ["lens", "camera", "angle", "frame"]
        ):
            risk += 1
        if agent == "Costume Designer" and any(
            term in lower for term in ["change costume", "new robe", "armor"]
        ):
            risk += 2
        if agent == "Continuity Supervisor" and any(
            term in lower for term in ["different", "new face", "change hair"]
        ):
            risk += 2
        if len(prompt) > 1200:
            risk += 1
        return risk

    def _recommendation(self, agent: str, risk: int) -> str:
        if risk < 2:
            return f"{agent} approves current branch."
        return f"{agent} recommends targeted revision before generation."


class SymbolicPromptLanguage:
    def compile_symbols(self, components: dict) -> dict:
        symbols = {
            "CHAR": self._id(components.get("character_database", {})),
            "ENV": self._id(components.get("environment_database", {})),
            "CAM": self._id(components.get("camera", {})),
            "LIGHT": self._id(components.get("film_bible", {}).get("film_lighting_style")),
            "STYLE": self._id(components.get("film_bible", {}).get("camera_rules")),
            "ACTION": self._id(components.get("user_instruction")),
        }
        compact = " ".join(f"{key}_{value}" for key, value in symbols.items() if value)
        return {
            "symbols": symbols,
            "compact_language": compact,
            "compiler_note": "Symbolic language stores stable intent tokens, then compiles to provider-specific English.",
        }

    def _id(self, value) -> str:
        if not value:
            return ""
        return str(abs(hash(str(value))) % 1000).zfill(3)
