# CMSC389A Course Mapping

App Factory maps directly to the course themes in CMSC389A.

## Prompt Engineering

Students can see how a natural language app idea is transformed into structured
requirements, architecture, and implementation tasks.

## AI-Assisted Development

The pipeline shows how AI can assist with planning, code generation, testing,
security review, documentation, and deployment.

## Architecture

The Architecture Agent produces framework, component, folder structure, data
flow, testing, deployment, and limitation decisions before code is generated.

## Next.js / Frontend

Generated apps use Next.js, TypeScript, and the App Router. This connects the
module to modern frontend development practices.

## Testing

The Testing Agent runs practical validation steps such as install, smoke tests,
and production builds when the runtime supports them.

## Security

The Security Agent checks for hardcoded secrets and dangerous client-side code
patterns. It also supports npm audit when a lockfile exists.

## Documentation

The Documentation Agent generates README, architecture, usage, limitations, and
deployment documentation for every generated app.

## Deployment

The Deployment Agent prepares Docker and Cloud Run deployment paths, reinforcing
how web apps move from local code to cloud services.

## Human-in-the-Loop AI

App Factory requires approval before code generation and before deployment. This
keeps the human responsible for important decisions.

## Responsible AI

The Scope Guard Agent rejects or simplifies unsafe or overly broad requests,
showing how AI systems can include policy and safety boundaries.

## Agentic Workflows

The module decomposes a large task into specialized agents:

- scope guard
- requirements
- architecture
- code generation
- testing
- security
- documentation
- deployment

