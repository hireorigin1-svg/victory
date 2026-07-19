# Phase 2: AI Research Mode

The architecture is frozen. New work must improve generation quality, reduce retries, lower cost, or improve human-calibrated quality.

## Rules

- No new database tables unless benchmark data proves they are necessary.
- No new services unless they can be evaluated against the north-star metric.
- Every experiment must be reproducible.
- Every improvement must pass the benchmark gate.
- Every report must be generated from stored experiments, benchmark runs, and dataset records.

## North Star

Average generations required to reach an approved shot.

Target: `2` or fewer.

## Research Loop

```text
Experiment Plan
Variation Generator
Benchmark Run
Automatic Scoring
Dataset Record
Prompt Gene Learning
Provider DNA
Monthly Report
Benchmark Gate
```

The goal is to discover what actually improves provider output, not to keep expanding architecture.
