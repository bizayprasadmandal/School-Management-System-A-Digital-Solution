# Development Setup Guide

## Prerequisites

- Docker Desktop 4.x + Docker Compose v2
- Node.js 20+ and npm 10+
- Python 3.12+ (for running tests outside Docker)
- Git

## Quick Start (Docker — recommended)

```bash
# 1. Clone
git clone https://github.com/your-org/edusphere-sms.git
cd edusphere-sms

# 2. Environment
cp backend/.env.example backend/.env
# Edit backend/.env — at minimum set SECRET_KEY

# 3. Start all services
docker compose up -d

# 4. First-time setup
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_demo_data
docker compose exec backend python manage.py createsuperuser

# 5. Optional: deepen the demo per role (see docs/SEEDING.md)
docker compose exec backend python scripts/seed_parent_children.py "Green Valley"
docker compose exec backend python scripts/seed_teacher_workspace.py "Green Valley"

# 6. Open browser
open http://localhost:5173              # React web app (Vite)
open http://localhost:8000/api/docs/    # Swagger UI (Authorize with a JWT)
open http://localhost:8000/api/redoc/   # ReDoc
open http://localhost:8000/api/schema/  # OpenAPI 3 document
open http://localhost:8000/admin/       # Django admin
open http://localhost:5555              # Celery Flower task monitor
open http://localhost:9001              # MinIO console (admin/admin)
```

Useful `make` targets: `up`, `down`, `logs`, `shell`, `migrate`, `seed`, `test`,
`test-cov`, `typecheck`, `lint`, `format`, `docs-serve`, `check-env` (see
`make help` for the full list, including the `prod-*` and `mobile-*` groups).

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL and Redis separately (or use docker compose for just those)
docker compose up -d postgres redis minio

python manage.py makemigrations  # only needed if you changed a model
python manage.py migrate        # 23 service apps ship their own trees (116 migration files)
python manage.py seed_demo_data
python manage.py runserver

# In another terminal — Celery worker
celery -A core worker -l debug

# In another terminal — Celery beat scheduler
celery -A core beat -l debug --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Frontend Web

```bash
cd frontend/web
npm install
cp .env.example .env.local
# Set REACT_APP_API_URL=http://localhost:8000/api/v1
npm run dev    # Vite dev server on http://localhost:5173
```

### Mobile

```bash
cd frontend/mobile
npm install
npx expo start
# Press 'a' for Android, 'i' for iOS (Mac only), or scan QR with Expo Go app
```

## Demo Login Credentials

| Role    | Email                                | Password     |
| ------- | ------------------------------------ | ------------ |
| Admin   | admin@demo.edusphere.school          | Admin@1234   |
| Teacher | sarah.mitchell@demo.edusphere.school | Teacher@1234 |
| Student | student001@demo.edusphere.school     | Student@1234 |
| Parent  | parent001@demo.edusphere.school      | Parent@1234  |

The full roster per school (including the bulk `demo.*` filler accounts that
**cannot** log in) is documented in `docs/DEMO_CREDENTIALS.md`.

## Running Tests

Run backend tests **inside the container that matches CI** — the project pins
black/isort/flake8 there, and running them on the Windows host produces line-end
differences that make pre-commit rewrite files in a loop.

```bash
# Backend — 974 tests, 59 files
docker exec sms_backend python -m pytest tests/ -q -p no:cacheprovider

# A subset while iterating
docker exec sms_backend python -m pytest tests/test_fees_and_gradebook.py -q -p no:cacheprovider

# Coverage (CI gate: --cov-fail-under=68)
docker exec sms_backend python -m pytest tests/ --cov=services --cov=core --cov-report=html

# Frontend — type check
cd frontend/web && npm run type-check

# Frontend — lint / unit tests
cd frontend/web && npm run lint && npm run test
```

Notes:

- `pytest.ini` sets `--reuse-db --timeout=120 --strict-markers --tb=short` and
  in-memory channels/cache for tests; markers are `slow`, `slow_axes`,
  `integration`.
- Settings default to `core.settings.base`; tests that hit the whole URL conf
  need `Client(SERVER_NAME="localhost")` or Django raises `DisallowedHost`.
- The OpenAPI regression suite (`tests/test_api_schema.py`) generates the ~7 MB
  schema once per session and takes ~6 minutes — don't run it casually.

Backend lint/pre-commit is configured at the repo root (`.pre-commit-config.yaml`,
black + isort + flake8 `--max-line-length=120`, `DJ01` ignored — the codebase
deliberately uses `null=True` on image/file fields).

## Load Testing

> 📖 **Full load test documentation is at `infrastructure/load-tests/README.md`**

k6 scripts simulate realistic user traffic against the API. Run them against
your local stack after seeding demo data:

```bash
# Seed demo data (if not already done)
docker compose exec backend python manage.py seed_demo_data

# Run the auth load test
cd infrastructure/load-tests
k6 run auth.js

# Run the attendance + fees load test
k6 run attendance.js
```

Thresholds are configured to fail if P(95) response times exceed 3 seconds
(auth) or 5 seconds (attendance).

## Database Backup Verification

> 📖 **Full backup docs are at `infrastructure/db/README.md`**

After creating a `pg_dump` backup, verify its integrity:

```bash
./infrastructure/db/verify_backup.sh /path/to/backup.sql.gz
```

This restores the backup to a temporary database and validates row counts
across 6 core tables.

## Code Structure Conventions

### Backend

- Each service lives in `services/<name>/` with `models.py`, `views.py`, `serializers.py`, `urls.py`, `tasks.py`, `signals.py`, `admin.py`, `tests/`
- All querysets are school-scoped — never forget `filter(school=request.user.school)`
- Use `@transaction.atomic` for any multi-step writes
- Background work always goes through Celery tasks

### Frontend

- Components in `components/common/` are role-agnostic
- Pages import from `../../api/hooks` (React Query) and `../../utils` (formatters)
- Never call `apiClient` directly from pages — always use hooks
- Use `useTitle(pageTitle)` at the top of every page component

## Environment Variables Reference

| Variable                   | Description                                                                              | Default         |
| -------------------------- | ---------------------------------------------------------------------------------------- | --------------- |
| `SECRET_KEY`               | Django secret key (50+ chars)                                                            | —               |
| `DEBUG`                    | Enable debug mode                                                                        | `False`         |
| `DATABASE_URL`             | PostgreSQL connection string                                                             | —               |
| `REDIS_URL`                | Redis connection string (`redis://redis:6379/0` in compose — published on host **6380**) | —               |
| `AWS_ACCESS_KEY_ID`        | S3/MinIO credentials                                                                     | —               |
| `AWS_SECRET_ACCESS_KEY`    | S3/MinIO credentials                                                                     | —               |
| `AWS_STORAGE_BUCKET_NAME`  | S3 bucket for documents                                                                  | `sms-documents` |
| `AWS_S3_ENDPOINT_URL`      | Override for MinIO in dev                                                                | —               |
| `USER_THROTTLE_RATE`       | Authenticated requests/hour, per user (see `docs/API.md`)                                | `6000/hour`     |
| `AUTH_LOGIN_THROTTLE_RATE` | Anonymous login attempts per minute                                                      | `10/minute`     |
| `REACT_APP_API_URL`        | Frontend API base URL (mapped to `VITE_API_URL` at build time)                           | —               |
| `REACT_APP_WS_URL`         | Frontend WebSocket base URL (mapped to `VITE_WS_URL` at build time)                      | —               |
| `EXPO_PUBLIC_API_URL`      | Mobile API base URL                                                                      | —               |
