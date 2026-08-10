# ─── Base stage ───────────────────────────────────────────────────────────────
FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ─── Development stage ────────────────────────────────────────────────────────
FROM base AS development

RUN pip install watchdog ipython django-debug-toolbar==4.2.0

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ─── Production stage ─────────────────────────────────────────────────────────
FROM base AS production

# Build args for collectstatic (passed from docker-compose; defaults keep the
# CI build hermetic — ARGs never persist into the image, runtime env from
# k8s/compose always overrides these).
ARG SECRET_KEY=build-time-placeholder-not-for-runtime
ARG DATABASE_URL=postgresql://build:build@localhost:5432/build_db
ARG REDIS_URL=redis://localhost:6379/0

# Create non-root user
RUN groupadd --gid 1001 django && \
    useradd --uid 1001 --gid django --shell /bin/bash --create-home django

COPY --chown=django:django . .

# Collect static (needs env vars to initialize Django settings)
# Collect static files to local filesystem during build (S3/MinIO not available at build time)
RUN SECRET_KEY=${SECRET_KEY} DATABASE_URL=${DATABASE_URL} REDIS_URL=${REDIS_URL} SENTRY_DSN= USE_S3=no \
    python manage.py collectstatic --noinput --settings=core.settings.production

USER django

EXPOSE 8000

# Gunicorn with uvicorn workers (ASGI for WebSocket support)
CMD ["gunicorn", "core.asgi:application", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "2", \
     "--worker-connections", "1000", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
