# Contributing to EduSphere SMS

Thanks for considering a contribution! This guide covers the basics.

## Getting Started

1. Fork the repository and clone your fork
2. Follow `docs/DEVELOPMENT.md` to set up your local environment
3. Create a feature branch: `git checkout -b feature/your-feature-name`

## Branch Naming

- `feature/*` — New functionality
- `fix/*` — Bug fixes
- `chore/*` — Tooling, dependencies, refactors
- `docs/*` — Documentation only

## Commit Messages

Write the subject as an imperative sentence describing the change and why it
matters — that is the style the existing history uses:

```
Fix teacher portal: real endpoints, award forms, workspace seeder
Serve a working OpenAPI schema and Swagger UI
```

[Conventional Commits](https://www.conventionalcommits.org/) prefixes are welcome
for new work; keep the body to a short paragraph on motivation, not a file list.

Add a `CHANGELOG.md` entry under `## [Unreleased]` for every user-visible change
before committing.

## Pull Request Process

1. Ensure `make test` and `make lint` pass locally (pre-commit runs the same
   black / isort / flake8 / prettier / bandit hooks — run `pre-commit run --all-files`)
2. Update the relevant documentation:
   - `docs/API.md` for endpoint changes (the live schema at `/api/docs/` is
     generated from the code, so the curated reference is what drifts)
   - `docs/SEEDING.md` for seeder or demo-data changes
   - `CHANGELOG.md` for every user-visible change
3. Add tests for new functionality — CI enforces
   `--cov-fail-under=68` (see `.github/workflows/ci-full.yml`)
4. Fill out the PR template completely
5. Request review from a maintainer
6. PRs require at least one approval and passing CI before merge

## Code Style

### Backend (Python)

- Format with `black` (line length 120)
- Sort imports with `isort`
- Type hints encouraged but not required everywhere
- Every service module follows the existing structure: `models.py`, `views.py`, `serializers.py`, `urls.py`, `tasks.py`, `signals.py`, `admin.py`

### Frontend (TypeScript/React)

- Functional components only, no class components
- Use hooks from `src/hooks/` and React Query from `src/api/hooks.ts` — never call `fetch` directly in components
- Tailwind utility classes; avoid inline styles except for dynamic values
- Run `npm run lint` and `npm run type-check` before committing
- Dev server: `npm run dev` (Vite on port 5173)

## Testing Requirements

- New backend endpoints require at least one test covering success + one covering permission denial
- Use `tests/factories.py` factories rather than manually constructing model instances
- Run `make test-cov` to verify coverage doesn't regress (CI gate: 68%)
- Run backend tests inside the stack that matches CI:
  `docker exec sms_backend python -m pytest tests/ -q -p no:cacheprovider`
- Frontend: `npm run type-check`, `npm run lint` and `npm run test` in `frontend/web`

## Reporting Issues

Please include:

- Steps to reproduce
- Expected vs actual behavior
- Environment (browser/OS for frontend, Python/Django version for backend)
- Relevant logs (`make logs-backend`)

## Code of Conduct

Be respectful, constructive, and patient. We're building software used by schools — quality and reliability matter more than speed.
