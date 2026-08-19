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

# 5. Open browser
open http://localhost:5173         # React web app (Vite)
open http://localhost:8000/api/docs/   # Swagger API docs
open http://localhost:8000/admin/      # Django admin
open http://localhost:5555         # Celery Flower task monitor
open http://localhost:9001         # MinIO console (admin/admin)
```

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL and Redis separately (or use docker compose for just those)
docker compose up -d postgres redis minio

python manage.py makemigrations  # generates real migrations for students/academics/etc.;
                                  # all 23 service apps ship their own migrations (53 files total)
python manage.py migrate
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

## Running Tests

```bash
# Backend — from backend/
pytest tests/ -v

# With coverage
pytest tests/ --cov=services --cov-report=html

# Frontend — type check
cd frontend/web && npm run type-check

# Frontend — lint
cd frontend/web && npm run lint
```

Backend lint/pre-commit is configured at the repo root (`.pre-commit-config.yaml`,
flake8 `--max-line-length=120`, `DJ01` ignored — the codebase deliberately uses
`null=True` on image/file fields).

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

| Variable                  | Description                                                         | Default         |
| ------------------------- | ------------------------------------------------------------------- | --------------- |
| `SECRET_KEY`              | Django secret key (50+ chars)                                       | —               |
| `DEBUG`                   | Enable debug mode                                                   | `False`         |
| `DATABASE_URL`            | PostgreSQL connection string                                        | —               |
| `REDIS_URL`               | Redis connection string                                             | —               |
| `AWS_ACCESS_KEY_ID`       | S3/MinIO credentials                                                | —               |
| `AWS_SECRET_ACCESS_KEY`   | S3/MinIO credentials                                                | —               |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket for documents                                             | `sms-documents` |
| `AWS_S3_ENDPOINT_URL`     | Override for MinIO in dev                                           | —               |
| `REACT_APP_API_URL`       | Frontend API base URL (mapped to `VITE_API_URL` at build time)      | —               |
| `REACT_APP_WS_URL`        | Frontend WebSocket base URL (mapped to `VITE_WS_URL` at build time) | —               |
| `EXPO_PUBLIC_API_URL`     | Mobile API base URL                                                 | —               |
