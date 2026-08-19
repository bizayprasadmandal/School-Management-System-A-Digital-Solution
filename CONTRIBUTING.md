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

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(attendance): add bulk leave approval endpoint
fix(gradebook): correct GPA rounding in report cards
docs(api): document WebSocket notification payload
```

## Pull Request Process

1. Ensure `make test` and `make lint` pass locally
2. Update relevant documentation (`docs/API.md` for endpoint changes)
3. Add tests for new functionality — aim for the existing coverage threshold (70%)
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
- Run `make test-cov` to verify coverage doesn't regress

## Reporting Issues

Please include:

- Steps to reproduce
- Expected vs actual behavior
- Environment (browser/OS for frontend, Python/Django version for backend)
- Relevant logs (`make logs-backend`)

## Code of Conduct

Be respectful, constructive, and patient. We're building software used by schools — quality and reliability matter more than speed.
