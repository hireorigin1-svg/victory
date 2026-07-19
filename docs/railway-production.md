# Railway Production Plan

Production target:

- Frontend: Railway service with root directory `frontend`
- Backend: Railway service with root directory `backend`
- Database: Railway PostgreSQL plugin
- File storage: Cloudflare R2 or any S3-compatible bucket, wired through the existing S3 environment variables
- Product name: Victory
- Higgsfield flow: manual copy/paste for v1
- Audience: internal tool

## Railway Services

Create one Railway project named `victory`.

Add these services:

1. `victory-backend`
   - Source root: `backend`
   - Build: Dockerfile
   - Public networking: enabled
   - Health check path: `/health`

2. `victory-frontend`
   - Source root: `frontend`
   - Build: Dockerfile
   - Public networking: enabled

3. `Postgres`
   - Railway PostgreSQL database

Railway supports monorepo deployments by setting a service root directory. Railway also exposes service variables to the build and runtime, and Railway Postgres provides `DATABASE_URL`.

## Backend Variables

Set these on `victory-backend`:

```env
APP_NAME=Victory
ENVIRONMENT=production
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=
JWT_SECRET_KEY=<generate-long-random-secret>
CORS_ORIGINS=["https://<victory-frontend-url>"]
ALLOW_PUBLIC_REGISTRATION=false
SEED_DIRECTOR_EMAIL=<your-admin-email>
SEED_DIRECTOR_PASSWORD=<temporary-strong-password>
ENABLE_REAL_LLM_CALLS=true
OPENAI_API_KEY=<your-openai-key>
OPENAI_MODEL=gpt-5-mini
ANTHROPIC_API_KEY=<your-anthropic-key>
ANTHROPIC_MODEL=claude-sonnet-4-5
AWS_ACCESS_KEY_ID=<r2-or-s3-access-key>
AWS_SECRET_ACCESS_KEY=<r2-or-s3-secret-key>
AWS_REGION=auto
S3_BUCKET=<bucket-name>
HIGGSFIELD_API_KEY=
```

For the first launch, `HIGGSFIELD_API_KEY` can stay empty because generation is manual.

## Frontend Variables

Set this on `victory-frontend`:

```env
NEXT_PUBLIC_API_BASE_URL=https://<victory-backend-url>
```

## First Launch Steps

1. Push this project to GitHub.
2. Create the Railway project.
3. Add Railway Postgres.
4. Add backend service from the GitHub repo, root `backend`.
5. Add frontend service from the same repo, root `frontend`.
6. Set backend variables.
7. Deploy backend and copy its public URL.
8. Set frontend `NEXT_PUBLIC_API_BASE_URL` to the backend URL.
9. Deploy frontend.
10. Open frontend and log in using `SEED_DIRECTOR_EMAIL` and `SEED_DIRECTOR_PASSWORD`.

## GitHub Auto-Deploy

The repository includes `.github/workflows/railway-deploy.yml`.

To enable it:

1. Open Railway dashboard.
2. Create a Railway project token for the `victory` project.
3. Open GitHub repo settings.
4. Add repository secret:

```env
RAILWAY_TOKEN=<railway-project-token>
```

After that, every push to `main` deploys both:

- `victory-backend`
- `victory-frontend`

Railway's direct GitHub repo-source connection for existing services must be configured in the Railway dashboard under each service's Source settings.

## What You Still Need To Provide

- Railway account access or a Railway project invite.
- GitHub repository access for this code.
- OpenAI API key.
- Anthropic API key.
- One admin email and temporary password.
- Optional: Cloudflare R2 account details for uploaded media storage.
