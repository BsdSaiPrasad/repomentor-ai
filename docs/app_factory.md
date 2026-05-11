# App Factory

App Factory is an agentic module inside RepoMentor AI that turns a safe natural
language app idea into a small generated Next.js application.

## Pipeline

```text
User app idea
-> Scope Guard Agent
-> Requirements Agent
-> Architecture Agent
-> Human approval checkpoint
-> Next.js Code Generator Agent
-> Testing Agent
-> Security Agent
-> Documentation Agent
-> Docker/Deployment Agent
-> Human approval checkpoint
-> Deploy to Google Cloud Run
-> Return final deployed link
```

## Safety Model

The Scope Guard Agent rejects or reduces requests involving:

- authentication
- payments
- banking
- medical, legal, or financial advice
- marketplaces
- complex SaaS
- real-time chat
- sensitive user data

Unsafe ideas are reduced to single-page, single-user demos when possible.

## Generated App Location

Generated apps are written to:

```text
generated_apps/<app_slug>/
```

Each app includes:

- Next.js App Router code
- TypeScript
- package.json
- tsconfig.json
- Dockerfile
- .dockerignore
- README.md
- architecture.md
- usage.md
- limitations.md
- deployment.md
- basic smoke tests when feasible

## Human Approval

App Factory has two approval points:

1. Before writing generated code
2. Before deploying to Cloud Run

Approvals are stored in memory for the first implementation. A future database
extension can persist approval events.

## Cloud Run Deployment

Deployment reads configuration from request fields or environment variables:

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GCP_ARTIFACT_REPOSITORY`

Secrets and GCP credentials must never be committed to the repo.

## Current Implementation Notes

- Groq is used for planning when available.
- Deterministic fallbacks keep demos usable during LLM failures or rate limits.
- Testing and security agents return structured results rather than crashing the
  full pipeline.
- Generated apps are intentionally small single-user demos.

