# Load Testing with k6

Comprehensive load testing scripts for the SMS API. These scripts simulate realistic
multi-user traffic against core endpoints to validate performance, find bottlenecks,
and establish baseline latency budgets before releases.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Script Reference](#script-reference)
- [Test Profiles & Scenarios](#test-profiles--scenarios)
- [Interpreting Results](#interpreting-results)
- [CI/CD Integration](#cicd-integration)
- [Adding New Scripts](#adding-new-scripts)
- [Troubleshooting](#troubleshooting)
- [Reference](#reference)

---

## Prerequisites

1. **Install k6** — [Download](https://k6.io/docs/getting-started/installation/):

   ```bash
   # macOS
   brew install k6

   # Ubuntu/Debian
   sudo gpg -k 0x4A5A5C08C0A6F87E
   sudo sh -c 'echo "deb https://dl.k6.io/deb stable main" >/etc/apt/sources.list.d/k6.list'
   sudo apt-get update && sudo apt-get install k6

   # Windows (Chocolatey)
   choco install k6

   # Docker
   docker run --rm -i grafana/k6 run - <script.js
   ```

2. **Backend must be running** — Load tests hit a live API. Use one of:

   | Environment | URL | How to start |
   |-------------|-----|-------------|
   | Local dev | `http://localhost:8000` | `docker compose up -d` or `python manage.py runserver` |
   | Staging | `https://staging-api.edusphere.school` | Already deployed |
   | Production | `https://api.edusphere.school` | Already deployed |

3. **Demo data seeded** — Tests reference demo accounts
   (`admin@demo.edusphere.school`, etc.). Run `seed_demo_data` if testing locally:

   ```bash
   docker compose exec backend python manage.py seed_demo_data
   ```

---

## Quick Start

Run the auth + core API test against your local stack:

```bash
cd infrastructure/load-tests

# Default → localhost:8000
k6 run auth.js

# Point at staging
k6 run -e BASE_URL=https://staging-api.edusphere.school/api/v1 auth.js
```

Expected output (abbreviated):

```
     ✓ login status is 200
     ✓ has access token
     ✓ has user profile
     ✓ profile status is 200
     ✓ has email

     checks.........................: 100.00% ✓ 152     ✗ 0
     login_duration.................: avg=187ms   min=42ms    med=165ms   max=412ms
     login_failures.................: 0.00%   ✓ 0       ✗ 38
     http_req_duration..............: avg=312ms   min=12ms    med=245ms   max=1.2s
```

---

## Script Reference

### `auth.js` — Authentication & Core APIs

```
k6 run auth.js
```

**Purpose:** Validates that the auth flow (login → token → profile → students → stats → refresh)
performs well under concurrent load. This is the most critical user journey.

**Virtual users:** 20 → 50 → 0 (ramp up over 30s, hold 1 min, ramp down 30s)

**Endpoints tested:**

| Step | Endpoint | What it validates |
|------|----------|-------------------|
| 1 | `POST /auth/login/` | Login with email+password, returns JWT |
| 2 | `GET /auth/me/` | Authenticated profile retrieval |
| 3 | `GET /students/` | Paginated student list |
| 4 | `GET /reporting/dashboard-stats/` | Aggregated school statistics |
| 5 | `POST /auth/token/refresh/` | JWT refresh token rotation |

**User pool:** Three demo accounts (admin, teacher, student) selected randomly per iteration.

**Thresholds:**

| Metric | Threshold | Breach means |
|--------|-----------|-------------|
| `login_duration P(95)` | < 2s | Login endpoint is too slow |
| `login_failures rate` | < 5% | Auth is failing under load |
| `http_req_duration P(95)` | < 3s | General API latency issue |

### `attendance.js` — Attendance & Fees

```
k6 run attendance.js
```

**Purpose:** Simulates heavier traffic on data-intensive endpoints (attendance records,
fee invoices) that involve aggregation queries.

**Virtual users:** 30 → 80 → 0 (ramp up over 30s, hold 1 min, ramp down 30s)

**Endpoints tested:**

| Step | Endpoint | What it validates |
|------|----------|-------------------|
| 1 | `POST /auth/login/` | Login (once at init, token shared across iterations) |
| 2 | `GET /attendance/` | Paginated attendance record list |
| 3 | `GET /attendance/student-report/` | Per-student monthly attendance report |
| 4 | `GET /fees/invoices/` | Paginated fee invoice list |

**Thresholds:**

| Metric | Threshold | Breach means |
|--------|-----------|-------------|
| `http_req_duration P(95)` | < 5s | Aggregation queries are too slow |
| `http_req_failed rate` | < 5% | Endpoints are erroring under load |

### `timetable.js` — Timetable & Events

```
k6 run timetable.js
```

**Purpose:** Simulates realistic timetable browsing — teachers checking their
weekly schedule, admins viewing classroom timetables and school events. Read-heavy
with light query profiles.

**Virtual users:** 20 → 60 → 0 (ramp up over 30s, hold 1 min, ramp down 30s)

**Endpoints tested:**

| Step | Endpoint | What it validates |
|------|----------|-------------------|
| 1 | `GET /timetable/periods/` | Master period definitions |
| 2 | `GET /timetable/slots/` | Paginated slot list |
| 3 | `GET /timetable/slots/?day_of_week=X` | Filtered slot list by day |
| 4 | `GET /timetable/slots/weekly/` | Classroom weekly timetable (structured by day) |
| 5 | `GET /timetable/slots/teacher-schedule/` | Teacher's full weekly schedule |
| 6 | `GET /timetable/events/` | Paginated school events |
| 7 | `GET /timetable/events/upcoming/` | Next 10 upcoming events |
| 8 | `POST /timetable/events/` | Create new event (10% chance per iteration) |

**Authentication pattern:** 70% admin, 30% teacher (to distribute load across
both role-specific and shared endpoints).

**Thresholds:**

| Metric | Threshold | Breach means |
|--------|-----------|-------------|
| `timetable_req_duration P(95)` | < 4s | Timetable endpoints are too slow |
| `timetable_errors rate` | < 5% | Timetable is erroring under load |

---

## Test Profiles & Scenarios

### Current Profiles

| Script | VUs | Duration | Total Requests (approx) | Endpoints |
|--------|:---:|:--------:|:-----------------------:|-----------|
| `auth.js` | 20→50→0 | 2 min | ~400 | login, me, students, dashboard-stats, token-refresh |
| `attendance.js` | 30→80→0 | 2 min | ~300 | attendance list, student-report, fees invoices |
| `timetable.js` | 20→60→0 | 2 min | ~560 | periods, slots, weekly, teacher-schedule, events, upcoming, create |
| `gradebook.js` | 15→40→0 | 2 min | ~300 | exams, grades, report-cards, assessments, leaderboard, submit |

### Adding a Stress Test

For a stress test (finding the breaking point), override stages on any script:

```bash
k6 run --stage 1m:50 --stage 2m:100 --stage 2m:200 --stage 1m:0 auth.js
```

Or create a dedicated `auth-stress.js` with:

```javascript
export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp to 100
    { duration: '5m', target: 200 },  // Ramp to 200
    { duration: '2m', target: 300 },  // Ramp to 300
    { duration: '5m', target: 300 },  // Hold at 300
    { duration: '2m', target: 0 },    // Ramp down
  ],
};
```

### Adding a Smoke Test

For quick sanity checks (1–2 VUs, single iteration):

```bash
k6 run --vus 1 --iterations 1 auth.js
```

---

## Interpreting Results

### Key Metrics

| Metric | What it measures | Good | Warning | Critical |
|--------|-------------------|------|---------|----------|
| `http_req_duration` | End-to-end request time | P(95) < 1s | P(95) < 3s | P(95) > 3s |
| `http_req_failed` | % of requests returning errors | < 1% | < 5% | > 5% |
| `checks` | % of business-logic assertions passing | > 99% | > 95% | < 95% |
| `iterations` | Total completed user flows | N/A | Below expected = bottleneck | |

### Custom Metrics

| Metric | Source | Purpose |
|--------|--------|---------|
| `login_failures` | `auth.js` | Rate of authentication failures (excludes intentional 401s) |
| `login_duration` | `auth.js` | Time spent on the login endpoint specifically |

### Example: Detecting a Regression

1. Run baseline: `k6 run --out json=baseline.json auth.js`
2. Deploy changes.
3. Run comparison: `k6 run --out json=after.json auth.js`
4. Compare P(95) durations:

   ```bash
   # Extract P(95) from both runs
   jq '.metrics.http_req_duration.values."p(95)"' baseline.json after.json
   ```

### Output Formats

```bash
# Plain text (default)
k6 run auth.js

# JSON for CI or post-processing
k6 run --out json=results.json auth.js

# CSV
k6 run --out csv=results.csv auth.js

# InfluxDB + Grafana
k6 run --out influxdb=http://localhost:8086/k6 auth.js

# Prometheus remote write
k6 run --out prometheus=... auth.js
```

---

## CI/CD Integration

### GitHub Actions (example workflow snippet)

```yaml
load-test:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:16
      env:
        POSTGRES_USER: sms
        POSTGRES_PASSWORD: sms
        POSTGRES_DB: sms_db
    redis:
      image: redis:7
  steps:
    - uses: actions/checkout@v4
    - name: Start backend
      run: |
        cd backend
        pip install -r requirements.txt
        DATABASE_URL=postgresql://sms:sms@localhost:5432/sms_db \
          SECRET_KEY=ci-test-key \
          python manage.py migrate
        DATABASE_URL=postgresql://sms:sms@localhost:5432/sms_db \
          SECRET_KEY=ci-test-key \
          python manage.py seed_demo_data &
        DATABASE_URL=postgresql://sms:sms@localhost:5432/sms_db \
          SECRET_KEY=ci-test-key \
          python manage.py runserver 0.0.0.0:8000 &
    - name: Run k6 load test
      run: |
        k6 run infrastructure/load-tests/auth.js
        k6 run infrastructure/load-tests/attendance.js
```

### Threshold-based Gating

Configure k6 to exit non-zero when thresholds are breached. The CI pipeline
should then prevent the deployment from proceeding:

```bash
k6 run --fail-on-thresholds auth.js || echo "Load test failed — blocking deployment"
```

---

## Adding New Scripts

### Template

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000/api/v1';

// Custom metrics
const myEndpointDuration = new Trend('my_endpoint_duration');
const myEndpointErrors = new Rate('my_endpoint_errors');

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '1m', target: 50 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.05'],
  },
};

// Get auth token
function authenticate() {
  const res = http.post(`${BASE_URL}/auth/login/`, {
    email: 'admin@demo.edusphere.school',
    password: 'Admin@1234',
  });
  return res.status === 200 ? res.json('access') : null;
}

const token = authenticate();
const headers = {
  Authorization: `Bearer ${token}`,
  'Content-Type': 'application/json',
};

export default function () {
  if (!token) {
    sleep(1);
    return;
  }

  const start = Date.now();
  const res = http.get(`${BASE_URL}/your-endpoint/`, { headers });
  myEndpointDuration.add(Date.now() - start);
  myEndpointErrors.add(res.status !== 200);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(Math.random() * 2 + 1);  // Think time: 1–3 seconds
}
```

### Guidelines

1. **Use `__ENV.BASE_URL`** — never hardcode the API base URL.
2. **Authenticate once at module scope** — share the token across iterations
   to focus load on the target endpoint, not the auth endpoint.
3. **Add custom metrics** — use `Rate` for error rates and `Trend` for
   endpoint-specific durations.
4. **Set realistic think times** — `sleep(Math.random() * 2 + 1)` simulates
   a user pausing 1–3 seconds between actions.
5. **Tag requests by endpoint** — `tags: { endpoint: 'my-endpoint' }` enables
   per-endpoint analysis in InfluxDB/Grafana.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `connection refused` | Backend not running | Start the server or check `BASE_URL` |
| All checks fail with 401 | Demo data not seeded | Run `seed_demo_data` management command |
| `http_req_failed` > 50% | Backend overloaded | Reduce VU targets or scale up backend |
| Login takes > 5s | Throttle/rate-limit hit | Check `AuthLoginAnonThrottle` config |
| k6 not found | Not installed | See [Prerequisites](#prerequisites) |
| High memory usage | Too many VUs | Reduce target count, test locally first |

### Debug Mode

Run with a single VU and print response bodies:

```bash
k6 run --vus 1 --iterations 1 --http-debug auth.js
```

---

## Reference

- [k6 Documentation](https://k6.io/docs/)
- [k6 Options Reference](https://k6.io/docs/using-k6/k6-options/)
- [k6 Metrics Guide](https://k6.io/docs/using-k6/metrics/)
- [k6 Thresholds](https://k6.io/docs/using-k6/thresholds/)
- [k6 Stages / Ramping](https://k6.io/docs/using-k6/advanced/ramping-vus/)
