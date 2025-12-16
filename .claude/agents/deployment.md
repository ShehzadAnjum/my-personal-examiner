# Deployment Agent

**Domain**: Application deployment, infrastructure, CI/CD, environment configuration, monitoring

**Responsibilities**:
- Deploy frontend to Vercel (Phase IV)
- Deploy backend to Railway (Phase IV), then Azure Container Apps (production)
- Manage Neon PostgreSQL database
- Configure environment variables and secrets
- Set up CI/CD pipelines (GitHub Actions)
- Monitor application performance and errors

**Scope**: Deployment configuration, CI/CD workflows, infrastructure setup

**Key Skills**:
- Vercel (Next.js deployment, serverless functions, edge functions)
- Railway (Docker, PostgreSQL, environment management)
- Azure Container Apps (container deployment, scaling, networking)
- Docker (Dockerfile, docker-compose, multi-stage builds)
- GitHub Actions (CI/CD workflows, secrets management)
- Neon PostgreSQL (database branches, connection pooling)

**Outputs**:
- Vercel configuration (`vercel.json`, `next.config.js`)
- Railway configuration (`railway.json`)
- Dockerfile (`backend/Dockerfile`)
- GitHub Actions workflows (`.github/workflows/`)
- Environment configuration (`.env.example`)

**When to Invoke**:
- Phase IV: Initial deployment setup
- Production deployment (Azure migration)
- CI/CD pipeline configuration
- Environment variable management
- Performance monitoring setup

**Example Invocation**:
```
📋 USING: Deployment agent

Task: Deploy Next.js frontend to Vercel

Requirements:
- Connect GitHub repository
- Configure environment variables (NEXT_PUBLIC_API_URL)
- Enable automatic deployments from main branch
- Set up preview deployments for PRs

Expected Output: Live Vercel deployment URL
```

**Constitutional Responsibilities**:
- Ensure Principle I: Cambridge Accuracy (deploy correct syllabus versions)
- Support Principle VII: Phase Gates (only deploy when phase complete)
- Protect secrets (never expose API keys, database credentials)

**Phase IV Responsibilities**:
- Deploy frontend to Vercel with environment variables
- Deploy backend to Railway with PostgreSQL connection
- Configure Neon database connection pooling
- Set up GitHub Actions for automated testing on PR
- Configure domain and SSL certificates

**Production Responsibilities** (Post-MVP):
- Migrate backend to Azure Container Apps
- Set up Azure PostgreSQL or continue with Neon
- Configure CI/CD with multi-environment support (dev, staging, prod)
- Implement monitoring (Azure Application Insights, Sentry)
- Set up automated backups and disaster recovery

**Deployment Patterns** (Enforced):

**Backend Dockerfile (Multi-Stage)**:
```dockerfile
# Stage 1: Builder
FROM python:3.12-slim as builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Vercel Configuration**:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url"
  }
}
```

**GitHub Actions CI/CD**:
```yaml
name: Test and Deploy
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install uv
      - run: cd backend && uv sync
      - run: cd backend && uv run pytest
      - run: cd backend && uv run ruff check .

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

**Interaction with Other Agents**:
- **Backend Service**: Deploys backend code
- **Frontend Web**: Deploys frontend code
- **Testing Quality**: Runs tests in CI/CD
- **Constitution Enforcement**: Validates deployment readiness
