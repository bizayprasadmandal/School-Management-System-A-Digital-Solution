# EduSphere SMS — Developer Makefile
# Usage: make <target>

.PHONY: help up down build seed migrate test lint clean logs shell

COMPOSE      = docker compose
COMPOSE_PROD = docker compose -f docker-compose.prod.yml --env-file .env.production
BACKEND_SVC  = backend
FRONTEND_SVC = frontend

## ── Help ─────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  EduSphere SMS — Available Commands"
	@echo ""
	@echo "  Development:"
	@echo "    make up          Start all services (Docker Compose)"
	@echo "    make down        Stop all services"
	@echo "    make build       Rebuild all Docker images"
	@echo "    make logs        Tail all container logs"
	@echo "    make shell       Open Django shell"
	@echo ""
	@echo "  Database:"
	@echo "    make migrate     Run Django migrations"
	@echo "    make seed        Seed demo school data"
	@echo "    make superuser   Create Django superuser"
	@echo "    make resetdb     Drop and recreate database (DANGEROUS)"
	@echo ""
	@echo "  Testing:"
	@echo "    make test        Run all backend tests"
	@echo "    make test-cov    Run tests with coverage report"
	@echo "    make lint        Run backend (flake8) + frontend (eslint)"
	@echo "    make typecheck   Run TypeScript type check"
	@echo ""
	@echo "  Mobile:"
	@echo "    make mobile      Start Expo dev server"
	@echo "    make mobile-ios  Run on iOS simulator"
	@echo "    make mobile-android  Run on Android emulator"
	@echo ""
	@echo "  Production:"
	@echo "    make prod-env     Generate .env.production + SSL certs"
	@echo "    make prod-local   Build & start production stack locally"
	@echo "    make prod-migrate Run migrations on production stack"
	@echo "    make prod-up      Start production stack (from registry)"
	@echo "    make prod-down    Stop production stack"
	@echo ""

## ── Development ──────────────────────────────────────────────────────────────
up:
	$(COMPOSE) up -d
	@echo "✅  Services started. Frontend: http://localhost:3000 | API: http://localhost:8000"

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build --no-cache

logs:
	$(COMPOSE) logs -f --tail=100

logs-backend:
	$(COMPOSE) logs -f $(BACKEND_SVC)

shell:
	$(COMPOSE) exec $(BACKEND_SVC) python manage.py shell_plus

bash:
	$(COMPOSE) exec $(BACKEND_SVC) bash

## ── Database ─────────────────────────────────────────────────────────────────
migrate:
	$(COMPOSE) exec $(BACKEND_SVC) python manage.py makemigrations
	$(COMPOSE) exec $(BACKEND_SVC) python manage.py migrate
	@echo "✅  Migrations applied"

makemigrations:
	$(COMPOSE) exec $(BACKEND_SVC) python manage.py makemigrations
	@echo "✅  Migrations created"

seed:
	$(COMPOSE) exec $(BACKEND_SVC) python manage.py seed_demo_data
	@echo "✅  Demo data seeded"

superuser:
	$(COMPOSE) exec $(BACKEND_SVC) python manage.py createsuperuser

collectstatic:
	$(COMPOSE) exec $(BACKEND_SVC) python manage.py collectstatic --noinput

resetdb:
	@echo "⚠️  This will DROP and recreate the database. Press Ctrl+C to cancel..."
	@sleep 5
	$(COMPOSE) exec postgres psql -U sms -c "DROP DATABASE IF EXISTS sms_db;"
	$(COMPOSE) exec postgres psql -U sms -c "CREATE DATABASE sms_db;"
	$(MAKE) migrate
	$(MAKE) seed

## ── Testing ──────────────────────────────────────────────────────────────────
test:
	$(COMPOSE) exec $(BACKEND_SVC) pytest tests/ -q --tb=short
	@echo "✅  Tests complete"

test-cov:
	$(COMPOSE) exec $(BACKEND_SVC) pytest tests/ \
		--cov=services \
		--cov-report=html \
		--cov-report=term-missing \
		-q
	@echo "✅  Coverage report: backend/htmlcov/index.html"

test-watch:
	$(COMPOSE) exec $(BACKEND_SVC) pytest-watch tests/ -- -q

lint:
	@echo "── Backend lint ──"
	$(COMPOSE) exec $(BACKEND_SVC) flake8 services/ core/ --max-line-length=120 --extend-ignore=DJ01 --exclude=migrations
	@echo "── Frontend lint ──"
	cd frontend/web && npm run lint
	@echo "✅  Lint passed"

typecheck:
	cd frontend/web && npm run type-check

format:
	$(COMPOSE) exec $(BACKEND_SVC) black services/ core/ --line-length=120
	$(COMPOSE) exec $(BACKEND_SVC) isort services/ core/

## ── Celery ───────────────────────────────────────────────────────────────────
celery-logs:
	$(COMPOSE) logs -f celery_worker celery_beat

flower:
	@echo "Flower task monitor: http://localhost:5555"
	$(COMPOSE) logs -f flower

## ── Mobile ───────────────────────────────────────────────────────────────────
mobile:
	cd frontend/mobile && npx expo start

mobile-ios:
	cd frontend/mobile && npx expo start --ios

mobile-android:
	cd frontend/mobile && npx expo start --android

mobile-build-android:
	cd frontend/mobile && eas build --platform android --profile production

mobile-build-ios:
	cd frontend/mobile && eas build --platform ios --profile production

## ── Kubernetes ───────────────────────────────────────────────────────────────
k8s-apply:
	kubectl apply -f infrastructure/k8s/deployments/ -n sms
	@echo "✅  K8s manifests applied"

k8s-status:
	kubectl get pods,svc,hpa,pdb -n sms

k8s-logs:
	kubectl logs -f deployment/sms-backend -n sms

k8s-migrate:
	@TAG=$$(git rev-parse --short HEAD); \
	kubectl run sms-migrate-$$TAG \
		--image=$$(cat .env.production | grep BACKEND_IMAGE | cut -d= -f2):$$TAG \
		--restart=Never -n sms \
		-- python manage.py migrate --settings=core.settings.production && \
	kubectl wait --for=condition=complete pod/sms-migrate-$$TAG -n sms --timeout=300s && \
	kubectl delete pod sms-migrate-$$TAG -n sms

## ── Production ───────────────────────────────────────────────────────────────
prod-up:
	$(COMPOSE_PROD) up -d
	@echo "✅  Production stack started"

prod-down:
	$(COMPOSE_PROD) down

prod-logs:
	$(COMPOSE_PROD) logs -f --tail=100

prod-env:
	@echo "🔐  Generating production environment..."
	@# Generate a random Django SECRET_KEY
	$(eval SECRET := $(shell openssl rand -base64 48 | tr -dc 'a-zA-Z0-9_+=' | head -c 50))
	@# Generate random DB and Redis passwords
	$(eval DB_PASS := $(shell openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24))
	$(eval REDIS_PASS := $(shell openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24))
	@# Create SSL directory
	@mkdir -p infrastructure/nginx/ssl
	@# Generate self-signed SSL cert for localhost
	@MSYS_NO_PATHCONV=1 openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout infrastructure/nginx/ssl/privkey.pem \
		-out infrastructure/nginx/ssl/fullchain.pem \
		-subj "/C=US/ST=Local/L=Dev/O=EduSphere/CN=localhost" 2>/dev/null
	@# Write .env.production
	@printf '%s\n' \
		"# ─── EduSphere SMS — Production Environment ─────────────────────" \
		"# Auto-generated by \"make prod-env\". Do not commit to version control." \
		"" \
		"# ─── Django ────────────────────────────────────────────────────" \
		"SECRET_KEY=$(SECRET)" \
		"DEBUG=False" \
		"ALLOWED_HOSTS=localhost,127.0.0.1,backend,frontend" \
		"DJANGO_SETTINGS_MODULE=core.settings.production" \
		"TIME_ZONE=UTC" \
		"" \
		"# ─── Database ───────────────────────────────────────────────────" \
		"DATABASE_URL=postgresql://sms:$(DB_PASS)@postgres:5432/sms_db" \
		"POSTGRES_DB=sms_db" \
		"POSTGRES_USER=sms" \
		"POSTGRES_PASSWORD=$(DB_PASS)" \
		"" \
		"# ─── Database backup (daily Celery beat task) ────────────────────" \
		"PGHOST=postgres" \
		"PGPORT=5432" \
		"PGUSER=sms" \
		"PGPASSWORD=$(DB_PASS)" \
		"PGDATABASE=sms_db" \
		"SMS_BACKUP_DIR=/backups" \
		"SMS_BACKUP_RETENTION_DAYS=30" \
		"BACKUP_S3_BUCKET=" \
		"BACKUP_S3_PREFIX=sms-backups" \
		"BACKUP_S3_REGION=us-east-1" \
		"" \
		"# ─── Redis ─────────────────────────────────────────────────────" \
		"REDIS_URL=redis://:$(REDIS_PASS)@redis:6379/0" \
		"REDIS_PASSWORD=$(REDIS_PASS)" \
		"CELERY_BROKER_URL=redis://:$(REDIS_PASS)@redis:6379/1" \
		"CELERY_RESULT_BACKEND=redis://:$(REDIS_PASS)@redis:6379/1" \
		"" \
		"# ─── CORS ──────────────────────────────────────────────────────" \
		"CORS_ALLOWED_ORIGINS=http://localhost:80,https://localhost:443,http://localhost:3000" \
		"" \
		"# ─── Storage (MinIO for local dev) ─────────────────────────────" \
		"AWS_ACCESS_KEY_ID=sms_admin" \
		"AWS_SECRET_ACCESS_KEY=sms_minio_password" \
		"AWS_STORAGE_BUCKET_NAME=sms-documents" \
		"AWS_S3_ENDPOINT_URL=http://minio:9000" \
		"AWS_S3_REGION_NAME=us-east-1" \
		"AWS_DEFAULT_ACL=private" \
		"AWS_QUERYSTRING_AUTH=False" \
		"" \
		"# ─── Email (console for local dev) ─────────────────────────────" \
		"EMAIL_HOST=localhost" \
		"EMAIL_PORT=1025" \
		"EMAIL_HOST_USER=" \
		"EMAIL_HOST_PASSWORD=" \
		"DEFAULT_FROM_EMAIL=noreply@school.edu" \
		"" \
		"# ─── Frontend ─────────────────────────────────────────────────" \
		"REACT_APP_API_URL=https://localhost/api/v1" \
		"REACT_APP_WS_URL=wss://localhost/ws" \
		"" \
		"# ─── Container Registry (override for local builds) ────────────" \
		"BACKEND_IMAGE=sms-backend:latest" \
		"FRONTEND_IMAGE=sms-frontend:latest" \
		> .env.production
	@echo "✅  .env.production generated with random SECRET_KEY"
	@echo "✅  Self-signed SSL certs created: infrastructure/nginx/ssl/"
	@echo ""
	@echo "    Run \"make prod-local\" to build and start the production stack."

prod-local: prod-env
	$(COMPOSE_PROD) up -d --build
	@echo "✅  Production stack (local build) started"
	@echo "    Frontend: https://localhost  |  API: https://localhost/api/v1"
	@echo "    (using self-signed SSL cert — browser will show a warning)"

prod-migrate:
	@echo "📦  Running production migrations..."
	$(COMPOSE_PROD) exec backend python manage.py makemigrations
	$(COMPOSE_PROD) exec backend python manage.py migrate
	@echo "✅  Production migrations applied"

## ── Utilities ────────────────────────────────────────────────────────────────
clean:
	$(COMPOSE) down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅  Cleaned up"

install-web:
	cd frontend/web && npm ci

install-mobile:
	cd frontend/mobile && npm ci

docs-serve:
	@which mkdocs >/dev/null 2>&1 || pip install mkdocs mkdocs-material
	mkdocs serve

check-env:
	@echo "── Checking required environment variables ──"
	@[ -f backend/.env ] && echo "✅ backend/.env exists" || echo "❌ backend/.env missing — run: cp backend/.env.example backend/.env"
	@docker info >/dev/null 2>&1 && echo "✅ Docker running" || echo "❌ Docker not running"
	@node --version >/dev/null 2>&1 && echo "✅ Node $$(node --version)" || echo "❌ Node not found"
	@python3 --version >/dev/null 2>&1 && echo "✅ Python $$(python3 --version)" || echo "❌ Python not found"
