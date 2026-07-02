# EduSphere SMS — Developer Makefile
# Usage: make <target>

.PHONY: help up down build seed migrate test lint clean logs shell

COMPOSE      = docker compose
COMPOSE_PROD = docker compose -f docker-compose.prod.yml
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
	@echo "    make prod-up     Start production stack"
	@echo "    make prod-down   Stop production stack"
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
	$(COMPOSE) exec $(BACKEND_SVC) flake8 services/ core/ --max-line-length=120 --exclude=migrations
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
