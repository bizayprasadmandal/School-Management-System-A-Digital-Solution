# High-Level Design (HLD) — EduSphere SMS

> **Version:** 2.0  
> **Date:** August 2026  
> **Status:** Current — URL schema, module counts and env matrix re-verified
> against the code on **2026-09-25**  
> **Target Market:** Private schools in Nepal (100–1,500 students)

---

## 1. System Overview

EduSphere is a **multi-tenant School Management System** serving private schools in
South Asia. It covers the complete student lifecycle — from admission application
through graduation — with localized payment gateways (Khalti, eSewa, Stripe),
multi-channel notifications, and role-based access for admins, teachers, students,
parents, accountants, librarians, and counselors.

### 1.1 Key Design Principles

| Principle                  | Implementation                                                                  |
| -------------------------- | ------------------------------------------------------------------------------- |
| **Multi-tenancy**          | Row-level isolation via `school_id` FK on every model + middleware enforcement  |
| **Self-describing API**    | OpenAPI 3 generated from the code at `/api/schema/`, Swagger UI at `/api/docs/` |
| **Monolith-first**         | Single Django deployment divided into service modules (not microservices)       |
| **Async by default**       | All I/O (email, SMS, push, PDF) offloaded to Celery workers                     |
| **Offline-capable mobile** | React Native + Expo with local cache for low-bandwidth schools                  |
| **Payment-localized**      | Stripe + Khalti + eSewa with per-school gateway toggles                         |
| **Defense in depth**       | JWT + 2FA + RBAC + tenant isolation + audit logging                             |

---

## 2. Architecture Patterns

### 2.1 Layered Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ React Web    │  │ React Native │  │ Public Application     │ │
│  │ (Vite + TS)  │  │ (Expo)       │  │ Portal (unauth)       │ │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬────────────┘ │
└─────────┼─────────────────┼──────────────────────┼───────────────┘
          │                 │                      │
          └─────────────────┴──────────┬───────────┘
                                       │ HTTPS / WSS
┌──────────────────────────────────────▼───────────────────────────┐
│                   API GATEWAY LAYER                               │
│              Nginx · Rate Limiting · TLS Termination              │
│              CORS · CSP · WebSocket Upgrade                       │
└──────────┬──────────────────────────────────────┬────────────────┘
           │                                      │
           ▼                                      ▼
   ┌───────────────┐                    ┌──────────────────┐
   │  REST API v1  │                    │   WebSocket      │
   │  (DRF + JWT)  │                    │   (Channels)     │
   │  /api/v1/*    │                    │   /ws/*          │
   └───────┬───────┘                    └────────┬─────────┘
           │                                     │
           └──────────────┬──────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────────┐
│                  APPLICATION LAYER (Django 5.2)                   │
│              Single deployable · Modular service apps              │
│                                                                   │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │  Auth   │ │ Students │ │Academics │ │Attendance│ │Gradebook│ │
│  │ 2FA/JWT │ │Enrollment│ │Subjects  │ │Daily/Per │ │Exams   │ │
│  │ RBAC    │ │Guardians │ │Teachers  │ │Leave     │ │Grades  │ │
│  └─────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │  Fees   │ │Admissions│ │   Comms  │ │Reporting │ │  HR    │ │
│  │Invoices │ │Public    │ │Announce  │ │Dashboard │ │Employees│ │
│  │Payments │ │Portal    │ │Messages  │ │PDF/CSV   │ │Payroll │ │
│  │Gateway  │ │Assessment│ │Notify    │ │Analytics │ │Leaves  │ │
│  └─────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │Timetable│ │  Library │ │  Hostel  │ │Transport │ │Sports  │ │
│  │Schedule │ │Books     │ │Rooms     │ │Routes    │ │Teams   │ │
│  │Events   │ │Checkout  │ │Alloc     │ │Vehicles  │ │Events  │ │
│  └─────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │Counsel  │ │Cafeteria │ │Behavior  │ │  Health  │            │
│  │Appts    │ │Meals     │ │Incidents │ │Clinic    │            │
│  │Referral │ │Plans     │ │Referral  │ │Records   │            │
│  └─────────┘ └──────────┘ └──────────┘ └──────────┘            │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐                         │
│  │  Alumni │ │Inventory │ │Conf equip│                         │
│  │Profiles │ │Stock/PO  │ │Bookings  │                         │
│  └─────────┘ └──────────┘ └──────────┘                         │
└─────────────────────────────┬────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────┐
│                       DATA TIER                                   │
│  ┌─────────────┐  ┌───────────┐  ┌────────────────────────────┐ │
│  │PostgreSQL 16│  │ Redis 7   │  │ S3 / MinIO                 │ │
│  │Primary DB   │  │ Cache+MQ  │  │ Documents · Media · Reports│ │
│  │PgBouncer    │  │ Channels  │  │ Backups                    │ │
│  └─────────────┘  └───────────┘  └────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Service Module Pattern

The backend is 23 school-scoped service modules (938 models, 116 migration
files, 4 407 URL patterns under `/api/`, 945 ViewSets, 975 serializers) plus a
`core` app that owns settings, tenant middleware, permissions, pagination, the
guardian-scoped portal views, and the OpenAPI schema customization.

Every service module follows a consistent internal structure:

```
services/<name>/
├── __init__.py
├── models.py          # Django ORM models (school-scoped)
├── serializers.py     # DRF serializers (read + write)
├── views.py           # ViewSets with RBAC permission classes
├── urls.py            # Router registration + custom endpoints
├── tasks.py           # Celery async tasks (email, PDF, notifications)
├── signals.py         # Django signals → Celery task dispatch
├── admin.py           # Django admin registration
├── apps.py            # App config + signal registration
└── migrations/
    └── 0001_initial.py
```

### 2.3 Design Patterns Used

| Pattern             | Where                      | Purpose                                                         |
| ------------------- | -------------------------- | --------------------------------------------------------------- |
| **Repository**      | ViewSets + serializers     | Encapsulate query logic behind clean API boundaries             |
| **Observer**        | Django signals → Celery    | Decouple request handling from side effects (email, push)       |
| **Strategy**        | Payment gateways           | Stripe/Khalti/eSewa interchangeable via config                  |
| **State Machine**   | Admissions workflow        | Enforce valid application transitions                           |
| **Decorator**       | RBAC permission classes    | Composable access control (`IsSchoolMember`, `IsAdmin`)         |
| **Factory**         | Test factories             | Consistent test data generation                                 |
| **Template Method** | PDF generation (ReportLab) | Shared report card/attendance template with per-school branding |

---

## 3. Component Diagram

### 3.1 Backend Components

```
┌─────────────────────────────────────────────────────────┐
│                    Django Application                      │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                  Middleware Stack                      │ │
│  │  CORS → Tenant → JWT → Axes → Audit → Security      │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌──────────────────┐  ┌──────────────────────────────┐  │
│  │   REST API Layer  │  │    WebSocket Layer            │  │
│  │   (DRF ViewSets)  │  │    (Django Channels)          │  │
│  │                    │  │                               │  │
│  │  • 105 ViewSets    │  │  • Notifications consumer     │  │
│  │  • 123 Serializers │  │  • Chat consumer              │  │
│  │  • 80 Router regs  │  │  • Typing indicators          │  │
│  └────────┬───────────┘  └────────────┬────────────────┘  │
│           │                            │                    │
│  ┌────────▼────────────────────────────▼────────────────┐  │
│  │              Service Layer (24 modules)               │  │
│  │  Each module: models → serializers → views → tasks   │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                 │
│  ┌────────────────────────▼─────────────────────────────┐  │
│  │              Celery Task Queue                        │  │
│  │  Queues: default, notifications, reports              │  │
│  │  Workers: horizontally scalable                       │  │
│  │  Beat: scheduled tasks (backup, expiry, reminders)   │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Frontend Components

```
┌──────────────────────────────────────────────────────────┐
│                   React Web App (Vite)                     │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                    Layout Layer                        │ │
│  │  AdminLayout · TeacherLayout · StudentLayout · ...    │ │
│  │  SidebarNav · Header · LanguageSwitcher               │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                    Page Layer                          │ │
│  │  admin/ · teacher/ · student/ · parent/ · public/     │ │
│  │  accountant/ · counselor/ · librarian/ · auth/         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                  Data Layer                            │ │
│  │  React Query (server state) · Zustand (UI state)     │ │
│  │  Axios client · WebSocket hook                        │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                 i18n Layer                             │ │
│  │  i18next + react-i18next (EN/NE)                      │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Data Flow Diagrams

### 4.1 Student Admission Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│Parent/   │────▶│ Public  │────▶│  Admin  │────▶│ Student │
│Student   │     │ Portal  │     │ Review  │     │ Account │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     ▼               ▼               ▼               ▼
  Apply ──▶  POST /public/apply/ ──▶ under_review ──▶ accepted
  Status ◀── GET /public/status/ ◀── shortlist   ◀── enrolled
             {application_number}      /waitlist       (student +
                                       or reject        guardian
                                                        accounts)
```

### 4.2 Fee Payment Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Student/ │────▶│ Invoice │────▶│ Payment │────▶│ Receipt │
│ Parent   │     │ Create  │     │ Gateway │     │ Generate│
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     ▼               ▼               ▼               ▼
  View inv ◀── Bulk generate ──▶ Stripe/Khalti ──▶ PDF receipt
  Pay online   (Celery task)     /eSewa webhook   + email
  Cash at desk                  Verify callback    + notification
```

### 4.3 Real-Time Notification Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Action  │────▶│ Signal  │────▶│ Celery  │────▶│ Channel │
│ (e.g.   │     │ Fire    │     │ Worker  │     │ Layer   │
│ attend.)│     │         │     │         │     │ (Redis) │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                                           │            │
                                           ▼            ▼
                                    ┌──────────┐  ┌──────────┐
                                    │ Email    │  │ WebSocket│
                                    │ SMS      │  │ Push     │
                                    │ (async)  │  │ (realtime│
                                    └──────────┘  └──────────┘
```

---

## 5. Integration Architecture

### 5.1 External Services

```
┌──────────────────────────────────────────────────────────────────┐
│                     EduSphere SMS                                  │
│                                                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │   Auth     │  │  Payment   │  │   Notify   │  │  Storage   │  │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  │
└────────┼───────────────┼───────────────┼───────────────┼──────────┘
         │               │               │               │
         ▼               ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │  Google  │   │  Stripe  │   │ SendGrid │   │AWS S3 /  │
   │  OAuth   │   │  Khalti  │   │ Twilio   │   │  MinIO   │
   │  (2FA)   │   │  eSewa   │   │ Firebase │   │          │
   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### 5.2 Integration Matrix

| Service          | Protocol           | Purpose             | Failure Mode                                        |
| ---------------- | ------------------ | ------------------- | --------------------------------------------------- |
| **Stripe**       | REST API + Webhook | Card payments       | Retry with exponential backoff; log failed webhooks |
| **Khalti**       | REST API + Verify  | Nepal mobile wallet | Verify callback; manual reconciliation on timeout   |
| **eSewa**        | REST API + Status  | Nepal e-wallet      | Status polling fallback; admin manual verification  |
| **SendGrid**     | SMTP / REST        | Transactional email | Fallback to console in dev; dead-letter queue       |
| **Twilio**       | REST API           | SMS notifications   | Retry 3x; log failures for admin review             |
| **Firebase FCM** | REST API           | Mobile push         | Token cleanup on invalid; batch delivery            |
| **Sentry**       | SDK                | Error tracking      | DSN-guarded init; no crashes if Sentry is down      |
| **Prometheus**   | Pull               | Metrics collection  | Alertmanager email on scrape failure                |

---

## 6. Deployment Architecture

### 6.1 Development (Docker Compose)

```
┌─────────────────────────────────────────────────┐
│              Docker Compose (local dev)           │
│                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Postgres │ │  Redis   │ │  MinIO   │          │
│  │  :5432   │ │ 6380→6379│ │ :9000/01 │          │
│  └──────────┘ └──────────┘ └──────────┘          │
│   (Redis is published on host :6380 so it does    │
│    not collide with other local stacks' :6379)    │
│                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Backend  │ │ Celery   │ │ Celery   │          │
│  │ Daphne   │ │ Worker   │ │ Beat     │          │
│  │  :8000   │ │          │ │          │          │
│  └──────────┘ └──────────┘ └──────────┘          │
│                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Frontend │ │  Nginx   │ │ Adminer  │          │
│  │ Vite     │ │  :80     │ │  :8081   │          │
│  │  :5173   │ │          │ │          │          │
│  └──────────┘ └──────────┘ └──────────┘          │
│                                                   │
│  ┌──────────┐                                    │
│  │ Flower   │                                    │
│  │  :5555   │                                    │
│  └──────────┘                                    │
└─────────────────────────────────────────────────┘
```

### 6.2 Production (Kubernetes)

```
┌──────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster (EKS/AKS/GKE)            │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Ingress (Nginx)                         │ │
│  │          TLS termination · Rate limiting · CORS            │ │
│  └──────────┬──────────────────────────────┬─────────────────┘ │
│             │                              │                    │
│  ┌──────────▼──────────┐    ┌──────────────▼────────────────┐ │
│  │   sms-backend       │    │   sms-frontend                 │ │
│  │   (Daphne ASGI)     │    │   (Nginx static + SPA)         │ │
│  │   HPA: 2-10 pods    │    │   HPA: 2-5 pods                │ │
│  └──────────┬──────────┘    └───────────────────────────────┘ │
│             │                                                  │
│  ┌──────────▼──────────┐    ┌──────────────────────────────┐ │
│  │   sms-celery-worker  │    │   sms-celery-beat             │ │
│  │   HPA: 2-8 pods     │    │   Single replica (leader)     │ │
│  └─────────────────────┘    └──────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │   Managed Services                                         │ │
│  │   RDS PostgreSQL · ElastiCache Redis · S3 Bucket          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │   Monitoring                                               │ │
│  │   Prometheus · Grafana · Alertmanager · Sentry             │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Security Architecture

### 7.1 Defense-in-Depth Layers

```
Layer 1: Network        → TLS (Ingress), VPN for admin access
Layer 2: API Gateway    → Rate limiting (50/hr anon, 500/hr auth), CORS, CSP
Layer 3: Authentication → JWT (60min access + 7-day refresh), 2FA (TOTP)
Layer 4: Authorization  → RBAC (7 roles), action allowlists, tenant isolation
Layer 5: Application    → Input validation (DRF serializers), SQL injection prevention (ORM)
Layer 6: Data           → Password hashing (PBKDF2), token digest (SHA-256), encryption at rest
Layer 7: Audit          → Immutable AuditLog for all sensitive operations
Layer 8: Monitoring     → Sentry errors, brute-force detection (django-axes)
```

### 7.2 Authentication Flow

```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│ Client │────▶│ Login  │────▶│  2FA   │────▶│ Access │
│        │     │ (email │     │ (TOTP/ │     │ Token  │
│        │     │ +pass) │     │ backup)│     │ (JWT)  │
└────────┘     └────────┘     └────────┘     └────────┘
                  │                │               │
                  ▼                ▼               ▼
            Axes throttle    Rate limit     Authorization
            (5 attempts/     (5 req/min)    (RBAC + tenant)
             30 min)
```

### 7.3 Tenant Isolation

```
Request → Middleware extracts X-School-ID header
        → IsSchoolMember permission checks user.school == request.school
        → ViewSet base_queryset filters by school_id
        → Super admins bypass for cross-school reporting
        → AuditLog records every cross-tenant access attempt
```

---

## 8. Scalability Considerations

### 8.1 Horizontal Scaling

| Component          | Scaling Strategy                         | Trigger                  |
| ------------------ | ---------------------------------------- | ------------------------ |
| **Django backend** | HPA (CPU 70%, memory 80%)                | Request latency increase |
| **Celery workers** | Independent HPA per queue                | Task queue depth         |
| **WebSocket**      | Sticky sessions + Redis fan-out          | Connection count         |
| **PostgreSQL**     | Read replicas via `DATABASE_REPLICA_URL` | Read query volume        |
| **Redis**          | Cluster mode (6+ nodes)                  | Memory usage > 80%       |
| **Static assets**  | CDN (CloudFront)                         | Origin request volume    |

### 8.2 Performance Budgets

| Metric                           | Target        | Current            |
| -------------------------------- | ------------- | ------------------ |
| P95 API latency                  | < 500ms       | ~312ms (load test) |
| P95 login latency                | < 2s          | ~187ms (load test) |
| Daily active students            | 50,000        | N/A (pre-pilot)    |
| Concurrent WebSocket connections | 1,000         | Tested             |
| Celery task throughput           | 100 tasks/sec | Redis-backed       |

### 8.3 Caching Strategy

| Cache Target              | TTL          | Invalidation                |
| ------------------------- | ------------ | --------------------------- |
| Dashboard stats           | 5 min        | On attendance/payment write |
| Student list (per page)   | 1 min        | React Query staleTime       |
| Fee invoice status        | 0 (no cache) | Always fresh                |
| Notification unread count | 30s          | On WebSocket event          |
| Grading scale lookup      | 1 hour       | On scale edit               |

---

## 9. Technology Stack Summary

| Layer             | Technology                       | Version    |
| ----------------- | -------------------------------- | ---------- |
| Backend framework | Django + DRF                     | 5.2 + 3.15 |
| Auth              | SimpleJWT + django-axes          | Latest     |
| Task queue        | Celery + django-celery-beat      | 5.x        |
| WebSocket         | Django Channels + channels-redis | 4.x        |
| Web frontend      | React + TypeScript + Vite        | 18 + 6.x   |
| State management  | TanStack Query + Zustand         | Latest     |
| Styling           | Tailwind CSS                     | 3.x        |
| i18n              | i18next + react-i18next          | Latest     |
| Mobile            | React Native + Expo              | SDK 50+    |
| Database          | PostgreSQL                       | 16         |
| Cache/queue       | Redis                            | 7          |
| Object storage    | AWS S3 / MinIO                   | Latest     |
| Container         | Docker + Kubernetes              | Latest     |
| CI/CD             | GitHub Actions                   | Latest     |
| Monitoring        | Prometheus + Grafana             | Latest     |
| Error tracking    | Sentry                           | Latest     |
| Load testing      | k6                               | Latest     |

---

## 10. Module Dependency Map

```
auth ─────────────────────────────────────────────────────────┐
  │ (User, School, JWT, 2FA, AuditLog)                        │
  │                                                            │
  ├─▶ students ──────────────────────────────────────────────┐│
  │     │ (Student, Guardian, Enrollment, Classroom)         ││
  │     │                                                     ││
  │     ├─▶ academics ─▶ timetable                           ││
  │     │   (Subject, Teacher)  (Slots, Events)              ││
  │     │                                                     ││
  │     ├─▶ attendance ─▶ communication                      ││
  │     │   (Records, Leave)  (Notify on absence)            ││
  │     │                                                     ││
  │     ├─▶ gradebook ─▶ reporting                           ││
  │     │   (Exams, Grades)  (Analytics, Export)              ││
  │     │                                                     ││
  │     ├─▶ fees ─▶ communication (payment notifications)    ││
  │     │   (Invoice, Payment, Gateway)                       ││
  │     │                                                     ││
  │     └─▶ admissions ─▶ communication (status emails)      ││
  │         (Application, Intake, Assessment)                 ││
  │                                                            ││
  ├─▶ hr ─▶ communication (payroll notifications)            ││
  │   (Employee, Salary, Payslip, Leave)                      ││
  │                                                            ││
  ├─▶ library, hostel, cafeteria, sports,                     ││
  │   transportation, health_clinic, counseling,              ││
  │   conferences, behavior, inventory, alumni                ││
  │   (each with own models + tasks)                          ││
  │                                                            ││
  └─▶ infrastructure ─▶ reporting (backup metrics)           ││
      (Celery tasks, backup, monitoring)                      ││
                                                               ││
  All services ──────────────────────────────────────────────┘│
  depend on auth for user/school scoping                       │
```

---

## Appendix A: URL Schema

There is **no `/api/v2/`** — `core/urls.py` mounts only `api/v1/`. Two prefixes
differ from their module name: `transport` (module `transportation`) and
`health` (module `health_clinic`).

| Prefix                                  | Service                                | Auth Required             |
| --------------------------------------- | -------------------------------------- | ------------------------- |
| `/api/v1/auth/`                         | Authentication, JWT, 2FA, audit log    | Partial (login is public) |
| `/api/v1/students/`                     | Student CRUD, guardians, enrollment    | Yes                       |
| `/api/v1/academics/`                    | Subjects, teacher assignments          | Yes                       |
| `/api/v1/attendance/`                   | Attendance records, leaves             | Yes                       |
| `/api/v1/gradebook/`                    | Exams, grades, report cards            | Yes                       |
| `/api/v1/timetable/`                    | Schedule slots, events                 | Yes                       |
| `/api/v1/communication/`                | Announcements, messages, notifications | Yes                       |
| `/api/v1/fees/`                         | Invoices, payments, scholarships       | Yes                       |
| `/api/v1/reporting/`                    | Dashboard stats, exports               | Yes                       |
| `/api/v1/hr/`                           | Employees, salary, payroll             | Yes                       |
| `/api/v1/admissions/`                   | Intakes, applications (admin)          | Yes                       |
| `/api/v1/admissions/public/`            | Public application portal + tracking   | **No**                    |
| `/api/v1/library/`                      | Book catalog, checkout                 | Yes                       |
| `/api/v1/hostel/`                       | Hostel rooms, allocations              | Yes                       |
| `/api/v1/transport/`                    | Routes, vehicles, driver schedules     | Yes                       |
| `/api/v1/cafeteria/`                    | Meal menus, bookings                   | Yes                       |
| `/api/v1/sports/`                       | Teams, events, achievements            | Yes                       |
| `/api/v1/counseling/`                   | Appointments, referrals                | Yes                       |
| `/api/v1/health/`                       | Health records, visits, immunizations  | Yes                       |
| `/api/v1/behavior/`                     | Incidents, points, referrals           | Yes                       |
| `/api/v1/conferences/`                  | Conference slots                       | Yes                       |
| `/api/v1/inventory/`                    | Items, stock, purchase orders          | Yes                       |
| `/api/v1/alumni/`                       | Alumni profiles, donations             | Yes                       |
| `/api/v1/infrastructure/`               | Assets, maintenance, backups           | Yes                       |
| `/api/v1/search/`                       | Global search (command palette)        | Yes                       |
| `/api/schema/`                          | OpenAPI 3 document                     | **No**                    |
| `/api/docs/`                            | Swagger UI                             | **No**                    |
| `/api/redoc/`                           | ReDoc                                  | **No**                    |
| `/health/live/`                         | Liveness probe                         | **No**                    |
| `/health/ready/`                        | Readiness probe (DB, cache, Celery)    | **No**                    |
| `/health/startup/`                      | Migration-state probe                  | **No**                    |
| `/metrics`                              | Prometheus scrape endpoint             | Network-restricted        |
| `/admin/`                               | Django admin                           | Staff                     |
| `/ws/notifications/`                    | WebSocket notifications                | Yes (JWT)                 |
| `/ws/chat/{recipient_id}/`              | WebSocket chat                         | Yes (JWT)                 |
| `/ws/attendance/{classroom_id}/{date}/` | Live attendance roster                 | Yes (JWT)                 |

---

## Appendix B: Environment Matrix

| Variable               | Dev (Docker)                                         | Staging             | Production           |
| ---------------------- | ---------------------------------------------------- | ------------------- | -------------------- |
| `DEBUG`                | `True`                                               | `True`              | `False`              |
| `DATABASE_URL`         | `postgresql://sms:sms_password@postgres:5432/sms_db` | RDS                 | RDS                  |
| `REDIS_URL`            | `redis://redis:6379/0`                               | ElastiCache         | ElastiCache          |
| `ALLOWED_HOSTS`        | `localhost,backend`                                  | `staging-api.*`     | `api.*`              |
| `EMAIL_BACKEND`        | `console`                                            | `smtp` (SendGrid)   | `smtp` (SendGrid)    |
| `SMS_PROVIDER`         | `console`                                            | `twilio`            | `twilio`             |
| `SENTRY_DSN`           | (empty)                                              | Set                 | Set                  |
| `USER_THROTTLE_RATE`   | `6000/hour`                                          | `6000/hour`         | tuned per deployment |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173`                              | `https://staging.*` | `https://app.*`      |
