# CineMind AI Director: Working MVP

## Delivered

- FastAPI backend with clean API, repository, schema, model, and service layers.
- JWT authentication with role-based access for `admin`, `director`, `editor`, and `viewer`.
- Character Database CRUD.
- Environment Database CRUD.
- Camera Database CRUD.
- Prop Database CRUD.
- Scene Database CRUD.
- Shot Database CRUD.
- Prompt Compiler that builds prompts from stored character, environment, camera, scene, prop, and previous-shot continuity.
- Prompt Compiler V2 with rule priorities: previous approved visual memory, Film Bible, character database, environment database, then user instruction.
- Director Engine that orchestrates script intake, scene planning, shot planning, prompt compilation, queue state, quality gate, approval, visual memory, and movie state.
- Film Bible singleton with relationships, locations, costumes, weapons, vehicles, lighting, palette, camera, lens, action, weather, timeline, and continuity rules.
- Visual Memory records approved-shot state as structured JSON and treats that memory as ground truth for later prompts.
- Continuity graph links shots through previous/next shot IDs and inherits from previous approved state.
- Movie state machine updates the current film state after every approved shot.
- Character Embedding Registry stores deterministic vectors now, ready to swap for provider-generated visual embeddings.
- Shot DNA records structured visual state for approved/generated shots: face geometry, costume, lighting, camera, environment, pose, and props.
- AI Critic reviews each generation as a continuity supervisor and writes corrected prompts.
- Prompt Evolution stores prompt V1/V2/V3 revisions and critic summaries.
- Director Feedback Loop generates, analyzes, critiques, rewrites, and repeats until continuity exceeds the target or attempts are exhausted.
- Experiment Database logs prompt hash, provider, model, scores, and acceptance outcome.
- Memory Graph records relationships between shots, costumes, environments, and scene facts.
- GenerationProvider interface supports mock, Higgsfield, Runway, Kling, Veo, and future providers.
- Prompt Genome decomposes every prompt into camera, lighting, emotion, costume, environment, style, verbs, adjectives, lens, composition, and motion genes.
- Prompt Scientist diagnoses which prompt gene likely caused continuity drift and recommends gene-level rewrites.
- Provider Behavior Database records how each provider/model/version responds to prompt genes and scores.
- Automatic A/B Testing compares prompt variants and keeps the higher-scoring experiment.
- Director Dashboard surfaces character/environment stability, provider success, retry averages, and learned behavior.
- Character Identity Model builds canonical profiles from approved images and embeddings.
- Scene Simulator predicts expected state and flags conflicts before generation.
- Production Analytics tracks retries, provider success, drift categories, and accepted-shot efficiency.
- Visual Scene Graph extracts entities, relations, pose, lighting, camera, lens, props, and environment from approved/generated images.
- Prompt AST stores prompts as editable branches for character, camera, lighting, environment, style, and motion.
- Visual Compiler turns story and shot intent into a cinematography-style visual plan before prompt generation.
- Reference Intelligence segments approved images into face, hair, costume, props, and background references.
- Multi-reference Optimization selects the best segment references for identity, costume, props, and environment per shot.
- Visual Diff Engine explains what changed between an approved shot and a candidate shot.
- Failure Clustering groups failed generations by face, costume, environment, lighting, and camera drift.
- Cinematography Engine stores real camera-language rules for styles such as Rajamouli, Nolan, and Mani Ratnam.
- Evaluation Framework seeds fixed benchmark films A-E and reruns them after pipeline changes.
- Automatic Scoring reports face, environment, costume, camera, lighting, motion, and overall benchmark scores.
- Human Review System captures 1-10 ratings and calibrates AI score against human judgment.
- Provider Capability Registry tracks image generation, image-to-video, references, seeds, resolutions, model versions, and costs.
- Dataset Collection stores generation inputs, outputs, scores, human ratings, acceptance, cost, and latency.
- North Star Metric: average generations required to reach an approved shot.
- Phase 2 Research Mode freezes architecture and focuses on measurable quality improvement.
- Autonomous Experiment Engine runs reproducible benchmark batches from controlled factor plans.
- Prompt Gene Learning estimates lift/drag for lens, lighting, motion, provider, prompt length, and reference-count genes.
- Provider DNA summarizes provider personality from observed behavior records.
- Monthly Research Report converts benchmark and experiment history into a research summary.
- Benchmark Gate compares baseline and candidate runs before accepting pipeline changes.
- Multi-Agent Debate reviews prompts with Director, Cinematographer, Costume Designer, Continuity Supervisor, and Critic votes.
- Symbolic Prompt Language compacts prompt intent into stable tokens before provider-specific English compilation.
- Vision Analyzer integration point that saves structured shot memory.
- Continuity Checker with face, clothing, environment, lighting, camera, and overall scoring.
- Auto-reject state when continuity drops below 90%.
- Redis/Celery worker scaffold for media-generation jobs.
- Version history snapshots on edits.
- PostgreSQL, Redis, backend, and frontend Docker Compose stack.
- Next.js console for login, creating all records, compiling shots, and reviewing stored continuity data.

## Local Run

```bash
docker compose up --build
```

Frontend: `http://localhost:3000`
Backend docs: `http://localhost:8000/docs`

Seeded director login:

```text
director@example.com
correct-horse-battery
```

## Provider Integrations

OpenAI, Claude, Higgsfield, and AWS S3 credentials should be supplied as environment variables before production deployment. The core app already stores provider outputs as URLs, structured JSON, prompt explanations, prompt genomes, behavior records, visual scene graphs, prompt ASTs, visual plans, reference segments, visual memories, embeddings, shot DNA, critic reviews, prompt evolution, experiments, graph facts, simulations, analytics, benchmark runs, human ratings, provider capabilities, dataset records, and continuity scores, so swapping deterministic local hooks for provider calls does not require a schema rewrite. Phase 2 should add no new tables unless benchmark evidence proves they are required.
