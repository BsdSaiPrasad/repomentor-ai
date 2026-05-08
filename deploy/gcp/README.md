## RepoMentor AI on GCP

This folder is a separate deployment path for GCP. It is designed to leave the
current local app untouched.

### What runs where

For the quickest safe rollout, use two Cloud Run services:

1. `repomentor-backend`
   - FastAPI app from `backend/main.py`
   - Handles Course Assistant, Assignment Builder, Repo Reviewer, MCP tools
   - Rebuilds the syllabus Chroma index on startup if `chroma_db/` is missing

2. `repomentor-frontend`
   - Next.js app from `frontend/`
   - Calls the backend through `REPOMENTOR_API_BASE_URL`

### Why we are doing it this way

- It does not change the local developer flow
- It works with the current code before a later Vertex AI migration
- Cloud Run gives you a public HTTPS URL without buying a domain

### Important current reality

The local app uses:

- Groq for generation
- local Chroma for syllabus retrieval
- optional Postgres for saved repo reviews

For the first GCP deploy:

- `GROQ_API_KEY` is required
- Postgres is optional
- Chroma will be rebuilt from `docs/syllabus.txt` and `docs/schedule.txt`

### What this first GCP deployment gives you

- A working online app
- Default HTTPS URLs like:
  - `https://repomentor-backend-xxxxx-uc.a.run.app`
  - `https://repomentor-frontend-xxxxx-uc.a.run.app`

### What this does NOT do yet

- Vertex AI embeddings / vector search
- BigQuery analytics
- custom domain

Those are phase 2 improvements after the first working deploy.

## GCP resources to create

Inside your GCP project, enable:

- Cloud Run
- Artifact Registry
- Cloud Build
- Secret Manager

Optional later:

- Cloud SQL
- BigQuery
- Vertex AI

## Backend environment variables

Required:

- `GROQ_API_KEY`

Optional:

- `DATABASE_URL`

## Frontend environment variables

Required:

- `REPOMENTOR_API_BASE_URL`
- `AUTH_SECRET`

Optional:

- `POSTGRES_URL`
- `DATABASE_URL`

The frontend build already skips DB migrations if `POSTGRES_URL` is not set.

## Manual deploy order

### 1. Deploy backend first

Build and deploy from the repo root:

```bash
gcloud run deploy repomentor-backend \
  --source . \
  --dockerfile deploy/gcp/backend.Dockerfile \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars PORT=8080 \
  --set-secrets GROQ_API_KEY=GROQ_API_KEY:latest
```

If you have a hosted Postgres later:

```bash
--set-secrets DATABASE_URL=DATABASE_URL:latest
```

### 2. Note the backend URL

Example:

```text
https://repomentor-backend-xxxxx-uc.a.run.app
```

### 3. Deploy frontend second

```bash
gcloud run deploy repomentor-frontend \
  --source . \
  --dockerfile deploy/gcp/frontend.Dockerfile \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars PORT=8080,REPOMENTOR_API_BASE_URL=https://repomentor-backend-xxxxx-uc.a.run.app,AUTH_SECRET=replace-me
```

You can later move `AUTH_SECRET` to Secret Manager too.

## Health checks to test

Backend:

- `/health`
- `/api/v1/status`

Frontend:

- `/`
- `/assignment-builder`
- `/repo-reviewer`
- `/developer-tools`

## Phase 2: better cloud architecture

After the first deploy works, the next clean upgrades are:

1. Replace local Chroma with Vertex AI embeddings + managed retrieval
2. Add Cloud SQL Postgres for app data
3. Export review data into BigQuery for analytics
4. Add GitHub Actions CI/CD for Cloud Run deploys

## CI/CD

This repo now includes:

- `.github/workflows/ci.yml`
  - runs lightweight checks on pull requests and non-`main` pushes
- `.github/workflows/deploy.yml`
  - deploys backend + frontend to Cloud Run on every push to `main`

### GitHub secrets to add

In your GitHub repo settings, add:

- `GCP_SA_KEY`
  - JSON key for a Google Cloud service account that can:
    - deploy Cloud Run
    - push to Artifact Registry
    - use service accounts
- `AUTH_SECRET`
  - a long random string for the frontend auth/session secret

### Recommended service account roles

The deployer service account should have:

- `Cloud Run Admin`
- `Artifact Registry Writer`
- `Service Account User`

If you later move more runtime secrets into Secret Manager, also add:

- `Secret Manager Secret Accessor`
