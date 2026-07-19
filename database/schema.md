# CineMind Sprint 1 Schema

Sprint 1 establishes the continuity backbone for characters, environments, and users.

## Tables

- `users`: authenticated operators with `admin`, `director`, `editor`, or `viewer` roles.
- `characters`: canonical visual and performance identity records.
- `environments`: canonical scene-space records for locations, lighting, weather, props, and references.
- `camera_profiles`: lens, movement, frame, motion, and look continuity records.
- `props`: weapons, vehicles, objects, positions, damage states, and references.
- `scenes`: script, timeline, linked characters, linked props, environment, and approved shot references.
- `shots`: compiled prompts, generated/approved media URLs, continuity scores, vision analysis, and approval state.
- `film_bibles`: one project-level source of truth for continuity, style, timeline, lighting, camera, weather, action, and palette rules.
- `visual_memories`: approved-shot visual state extracted from generated images.
- `movie_states`: current state-machine snapshot of the film plus history.
- `character_embeddings`: persistent visual identity vectors for canonical character comparison.
- `environment_embeddings`: persistent environment identity vectors.
- `shot_dna`: structured approved/generated visual state for each shot.
- `critic_reviews`: continuity-supervisor critiques and corrected prompts.
- `prompt_evolutions`: prompt revision history across feedback-loop attempts.
- `generation_experiments`: data-driven prompt/provider experiment log.
- `memory_graph_nodes` and `memory_graph_edges`: relationship memory for facts such as costume, location, damage, repair, and scene introduction.
- `prompt_genomes`: structured prompt genes used for research.
- `provider_behavior_records`: observed provider/model behavior and learned rules.
- `ab_test_groups`: prompt variant experiments and winners.
- `character_identity_profiles`: canonical identity profile learned from approved images.
- `scene_simulations`: expected state and conflict detection before generation.
- `production_metrics`: aggregate production and cost metrics.
- `visual_scene_graphs`: extracted visual entities, relations, and shot attributes.
- `prompt_asts`: prompt abstract syntax trees for branch-level edits.
- `visual_plans`: cinematography-aware pre-prompt shot plans.
- `reference_assets` and `reference_segments`: approved image references and segment embeddings.
- `reference_selections`: optimized multi-reference sets for a shot.
- `visual_diffs`: pixel-independent continuity diffs and corrections.
- `failure_clusters`: clustered failure modes across generations.
- `cinematography_styles`: reusable camera, lighting, and composition rules.
- `benchmark_projects`: fixed benchmark film definitions.
- `benchmark_runs`: provider/pipeline benchmark executions.
- `benchmark_shot_scores`: per-shot automatic evaluation scores.
- `human_reviews`: 1-10 human ratings and AI calibration deltas.
- `provider_capabilities`: provider/model feature matrix.
- `generation_dataset_records`: full research dataset records with inputs, outputs, scores, cost, latency, and human ratings.

Continuity records include JSON history/memory fields so the Director Engine can prioritize approved visual memory and Film Bible rules over fresh user text.
