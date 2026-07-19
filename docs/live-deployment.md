# Live Deployment Guide

## What is ready

CineMind AI Director is now a working full-stack MVP:

- Authenticated director console.
- PostgreSQL-backed continuity database.
- Character, environment, camera, prop, scene, and shot CRUD APIs.
- Prompt Compiler that builds prompts from stored continuity data.
- Prompt Compiler V2 with rule priorities and warning output.
- Film Bible module.
- Director Engine orchestration endpoint.
- Visual Memory and Movie State persistence.
- Character Embedding Registry hook.
- Shot DNA, AI Critic, Prompt Evolution, Director Feedback Loop, Memory Graph, and Experiment Database.
- Provider abstraction for Higgsfield, Runway, Kling, Veo, and future models.
- Sprint 4 AI Research Layer: prompt genome, prompt scientist, provider behavior database, automatic A/B tests, scene simulator, canonical identity, and production analytics.
- Sprint 5 Visual Intelligence: scene graph extraction, prompt AST, visual compiler, reference segmentation/selection, multi-reference optimization, visual diff, failure clustering, and cinematography style rules.
- Sprint 6 Evaluation Framework: benchmark films, automatic scoring, human reviews, provider capabilities, dataset collection, and north-star tracking.
- Phase 2 AI Research Mode: architecture freeze, autonomous experiment batches, prompt-gene learning, provider DNA, monthly reports, benchmark gates, multi-agent debate, and symbolic prompt language.
- Vision Analyzer integration point.
- Continuity Checker and auto-reject scoring.
- Redis/Celery worker for provider jobs.
- Docker production stack.

## Deploy on a Docker server

1. Copy `.env.example` to `.env`.
2. Replace all secrets and provider keys.
3. Set:

```text
POSTGRES_USER=cinemind
POSTGRES_PASSWORD=<strong password>
POSTGRES_DB=cinemind
JWT_SECRET_KEY=<long random secret>
CORS_ORIGINS=["https://your-domain.com"]
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
```

4. Start production:

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

5. Point your domain or reverse proxy to:

```text
Frontend: port 3000
Backend: port 8000
```

## Provider keys

The MVP runs without OpenAI, Claude, Higgsfield, or S3 credentials. Add those keys before enabling real media generation. The database and APIs already store prompt decisions, generated media URLs, approved media URLs, vision analysis, and continuity scores.
