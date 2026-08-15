# Observability — Sentry Error Tracking & Alerts

Sentry is the error-tracking layer for the stack. The Prometheus/Grafana stack
covers metrics; Sentry covers **who hit what error, when** across backend,
workers, and the web app.

## What is already wired

| Layer                             | Where                                 | Status                                                                                                                                                                         |
| --------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Backend (Django + Celery + Redis) | `backend/core/settings/production.py` | ✅ init guarded by `SENTRY_DSN`; Django/Celery/Redis integrations; `traces_sample_rate=0.1`; `environment="production"`                                                        |
| Web (React)                       | `frontend/web/src/index.tsx`          | ✅ init **only when `REACT_APP_SENTRY_DSN` is set** — no hardcoded DSN, dev/CI builds stay Sentry-free; tracing + session replay                                               |
| Mobile (React Native/Expo)        | `frontend/mobile/App.tsx`             | ✅ JS-level capture, guarded by `EXPO_PUBLIC_SENTRY_DSN` (`enableNative: false` — works in Expo Go); native crash reports need an EAS build + config plugin (see “Next” below) |

**Release tracking:** the backend uses `APP_VERSION`; the web image bakes
`REACT_APP_SENTRY_RELEASE=<git sha>` from the CI build. Errors in production are
attributable to a specific commit.

## Celery worker logs (structured JSON)

Workers route **every** log line through Django's `LOGGING` via the
`setup_logging` signal in `backend/core/celery.py` — Celery's default handler
hijack is disabled, so the `celery.*` runtime loggers, `services.*` task
modules, and `celery.task` all emit with the project's configured formatters.

In production each line is **one JSON object** on stdout with fields
`asctime levelname name process message pathname lineno`, plus any `extra`
context task modules attach (e.g. `{"invoice_count": n}`) as real fields.

**Task failures:** the `task_failure` signal in `core/celery.py` logs a
structured error carrying `task`, `task_id`, `task_args`/`task_kwargs`
(PII-redacted, truncated), `retries`, `queue`, and the full traceback. The same failure is
forwarded to **Sentry by the `CeleryIntegration`** (enabled in
`core/settings/production.py`) whenever `SENTRY_DSN` is set — so every worker
error is both queryable in logs and alerted on.

```bash
# Follow live worker logs as JSON, one object per line (docker compose)
docker compose logs -f celery_worker | jq -R 'fromjson?'

# Show recent task failures with their payloads (k8s — match your deployment)
kubectl logs -n sms -l app=sms-celery-worker | grep '"celery.task"' | jq -R 'fromjson?'
```

(The `-l` label selector is robust to deployment-name changes; adjust the
label to whatever the worker Deployment actually carries.)

## Env vars / GitHub secrets

| Env var                        | Where                              | Notes                                                                             |
| ------------------------------ | ---------------------------------- | --------------------------------------------------------------------------------- |
| `SENTRY_DSN`                   | backend container (prod + staging) | Unset → backend runs without Sentry                                               |
| `REACT_APP_SENTRY_DSN`         | web build (GitHub secret)          | Unset → Sentry disabled in the image (empty is a valid state, not a broken image) |
| `REACT_APP_SENTRY_DSN_STAGING` | staging web build (secret)         | Same, for `deploy-staging.yml`                                                    |
| `REACT_APP_SENTRY_RELEASE`     | web build                          | Auto-set to `GITHUB_SHA` by the `fe-args` step — no action needed                 |
| `SENTRY_AUTH_TOKEN`            | your machine only                  | Needed only for the API alert-rule curl below                                     |

## Getting a DSN (one-time)

1. Create a project at https://sentry.io — one for **edusphere-web**, one for
   **edusphere-backend** (or a single project; the DSN determines which project
   events land in).
2. **Settings → Projects → `<project>` → Client Keys (DSN)** → copy the DSN.
3. Backend: set `SENTRY_DSN` in the deployed environment / k8s secret.
4. Web: add the DSN as a GitHub secret `REACT_APP_SENTRY_DSN`
   (+ `REACT_APP_SENTRY_DSN_STAGING` for staging) — the next `docker-build`
   bakes it in.

## Alert rules — make it actually ping you

Configure in **Alerts → Create Alert Rule** per project (≈2 minutes each).
These are the three that matter:

| Alert           | Trigger                                 | Action                     | Severity |
| --------------- | --------------------------------------- | -------------------------- | -------- |
| **New issue**   | Any issue is created for the first time | Email **+ Telegram/Slack** | P1       |
| **Regression**  | An issue that was resolved reappears    | Email **+ Telegram/Slack** | P1       |
| **High volume** | > 50 events in 15 minutes (any issue)   | Email only                 | P2       |

Suggested settings (web project):

- _Conditions:_ "An issue is created" → notify immediately (don't wait for
  "more than X events" — you want first sighting).
- _Actions:_ Email `you@…` and add a **Telegram bot** via **Settings →
  Integrations → Telegram** (or Slack, Discord) so alerts land on your phone.
- _Also tick_ **"Send notification when an issue is resolved / regressed"**
  under **Issue → Rules** (this powers the Regression alert).

### Same alerts via API (optional)

With a `SENTRY_AUTH_TOKEN` (Settings → Auth Tokens → `project:read`,
`alerts:write`):

```bash
# List projects (to confirm org/project slugs)
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  https://sentry.io/api/0/organizations/<org>/projects/

# Create the "new issue" alert rule
curl -s -X POST -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" -H "Content-Type: application/json" \
  https://sentry.io/api/0/projects/<org>/<project>/alert-rules/ \
  -d '{
    "name": "EduSphere: New issue",
    "conditions": [{"name": "sentry.rules.conditions.first_seen_event.FirstSeenEventCondition"}],
    "actions": [{"name": "sentry.rules.actions.notify_event.NotifyEventAction"}],
    "actionMatch": "all",
    "frequency": 60
  }'
```

## What to do when an alert fires

1. Read the issue — the stack trace links to the exact commit via the release.
2. For backend errors, check the associated k8s pod logs (`kubectl logs -n sms
deploy/sms-backend`) and the Grafana dashboards for the same window.
3. Fix → deploy → **mark resolved** in Sentry (the Regression alert will catch
   it if the fix doesn't hold).

## Backup health alerts (Prometheus)

Automated S3 backups are watched by `infrastructure/monitoring/rules/backup_alerts.yml`
(backup not found / too old / S3 push failure). Alerts land in Alertmanager; see
`docs/DEPLOYMENT.md` → "Automated Backups" for the schedule and S3 config.

## Next (when you care)

- **Mobile native crash reports:** currently JS-level only (`enableNative:
false`). For native crashes, add the `@sentry/react-native/expo` config
  plugin to `app.json`, drop `enableNative` in `App.tsx`, and build with EAS.
- **Session replay:** already enabled on the web (10% prod) — turn it up after
  you confirm volume/quotas.
- **Log shipping:** when the cluster has a log sink (CloudWatch/Loki), send the
  worker's JSON stdout there — the fields are already structured for it.
