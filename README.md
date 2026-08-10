# 🎓 EduSphere — School Management System v2.0

A production-grade, multi-tenant School Management System built with Django, React, and React Native.

[![CI](https://github.com/bizayprasadmandal/School-Management-System-A-Digital-Solution/actions/workflows/ci-full.yml/badge.svg?branch=main)](https://github.com/bizayprasadmandal/School-Management-System-A-Digital-Solution/actions/workflows/ci-full.yml)
[![codecov](https://codecov.io/gh/bizayprasadmandal/School-Management-System-A-Digital-Solution/branch/main/graph/badge.svg)](https://codecov.io/gh/bizayprasadmandal/School-Management-System-A-Digital-Solution)

---

## 📐 Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │  React Web App  │  │  iOS App (RN)   │  │  Android App (RN)       │  │
│  │  (TypeScript)   │  │                 │  │                         │  │
│  └────────┬────────┘  └────────┬────────┘  └────────────┬────────────┘  │
└───────────┼────────────────────┼────────────────────────┼───────────────┘
            │                    │                        │
            └────────────────────┴──────────┬─────────────┘
                                            │ HTTPS / WSS
┌───────────────────────────────────────────▼───────────────────────────────┐
│                         API GATEWAY (Nginx + K8s Ingress)                  │
│                    Rate limiting · TLS · Load Balancing                    │
└──────┬─────────────────────┬─────────────────────────────┬────────────────┘
       │                     │                             │
       ▼                     ▼                             ▼
 REST API v1/v2          GraphQL                      WebSocket
  (DRF + JWT)         (Graphene)                  (Django Channels)
       │                     │                             │
       └─────────────────────┴─────────────────────────────┘
                                     │
┌────────────────────────────────────▼───────────────────────────────────────┐
│                         MICROSERVICES LAYER (Django)                        │
│                                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  Auth    │ │ Students │ │Academics │ │Attendance│ │   Gradebook      │ │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │ │   Service        │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────────────────┐  │
│  │Timetable │ │  Comms   │ │  Fees    │ │      Reporting Service       │  │
│  │ Service  │ │ Service  │ │ Service  │ │  (PDF · CSV · Analytics)     │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────────────────┘  │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼───────────────────────────────────────┐
│                              DATA TIER                                      │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────────────────────┐ │
│  │  PostgreSQL 16   │  │  Redis 7     │  │  S3 / MinIO Object Storage     │ │
│  │  (Primary DB)    │  │  (Cache+MQ)  │  │  (Documents · Media · Reports) │ │
│  └─────────────────┘  └──────────────┘  └────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗂 Project Structure

```
school-management-system/
├── backend/                          # Django backend
│   ├── core/                         # Project config, URLs, middleware
│   │   ├── settings/                 # base, development, production
│   │   ├── permissions.py            # RBAC permission classes
│   │   ├── pagination.py             # Custom paginators
│   │   └── exceptions.py            # Global exception handler
│   ├── services/                     # Independent service modules
│   │   ├── auth/                     # User, School, JWT, 2FA
│   │   ├── students/                 # Students, Guardians, Enrollments
│   │   ├── academics/                # Subjects, Teacher Assignments, Lesson Plans
│   │   ├── attendance/               # Daily + period attendance, Leaves
│   │   ├── gradebook/                # Exams, Grades, Assessments, Report Cards
│   │   ├── timetable/                # Schedule slots, School Events
│   │   ├── communication/            # Announcements, Messages, Notifications
│   │   ├── reporting/                # Analytics, PDF/CSV exports
│   │   └── fees/                     # Invoices, Payments, Scholarships
│   └── api/graphql/                  # Unified GraphQL schema
│
├── frontend/
│   ├── web/                          # React 18 + TypeScript web app
│   │   └── src/
│   │       ├── api/                  # Axios client + React Query hooks
│   │       ├── components/           # Shared UI components
│   │       ├── pages/                # Role-based page modules
│   │       │   ├── admin/            # Admin pages (dashboard, students...)
│   │       │   ├── teacher/          # Teacher pages
│   │       │   ├── student/          # Student pages
│   │       │   └── parent/           # Parent pages
│   │       ├── store/                # Zustand state stores
│   │       └── types/                # Full TypeScript type definitions
│   └── mobile/                       # React Native app (iOS + Android)
│       └── src/
│           ├── navigation/           # Stack + Tab navigators per role
│           └── screens/              # Screen components per role
│
└── infrastructure/
    ├── k8s/                          # Kubernetes manifests
    │   └── deployments/              # Backend, Celery, Frontend deployments
    ├── docker/                       # Dockerfiles (multi-stage)
    └── nginx/                        # Reverse proxy config
```

---

## 🚀 Quick Start (Docker Compose)

```bash
# 1. Clone and enter
git clone https://github.com/bizayprasadmandal/School-Management-System-A-Digital-Solution.git
cd School-Management-System-A-Digital-Solution

# 2. Copy environment files
cp backend/.env.example backend/.env

# 3. Start all services
docker compose up -d

# 4. Run migrations (they ship with every service) + seed data
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_demo_data    # demo school with realistic data
docker compose exec backend python manage.py createsuperuser

#    Optional seeds — run as needed:
#    docker compose exec backend python manage.py seed_operational_data    # current academic year, exams, HR, admissions, events
#    docker compose exec backend python manage.py seed_additional_schools  # extra schools + admins (multi-school demo)
#    docker compose exec backend python manage.py seed_e2e_data            # exact Playwright e2e accounts (idempotent)

# 5. Open browser
open http://localhost:3000
```

---

## 🔐 User Roles & Access

| Role         | Dashboard   | Students        | Grades          | Attendance     | Fees          | Reports        |
| ------------ | ----------- | --------------- | --------------- | -------------- | ------------- | -------------- |
| Super Admin  | ✅ Full     | ✅ All schools  | ✅ All          | ✅ All         | ✅ All        | ✅ All         |
| School Admin | ✅ School   | ✅ Own school   | ✅ Own school   | ✅ Own school  | ✅ Own school | ✅ Own school  |
| Teacher      | ✅ Limited  | 👁 Own classes  | ✏️ Own subjects | ✏️ Own classes | ❌            | ❌             |
| Student      | ✅ Personal | 👁 Own profile  | 👁 Own grades   | 👁 Own         | 👁 Own        | ❌             |
| Parent       | ✅ Personal | 👁 Own children | 👁 Children's   | 👁 Children's  | 💳 Pay        | ❌             |
| Accountant   | ❌          | ❌              | ❌              | ❌             | ✅ Full       | ✅ Fee reports |

---

## 🧩 Core Modules

### 1. Student Information Management

- Complete student lifecycle: enrollment → promotion → graduation
- Guardian/parent portal with multi-child support
- Document vault (birth certs, transfer certificates, etc.)
- Medical records and emergency contacts

### 2. Academic Management

- Subject setup per grade with credit hours and pass marks
- Teacher-subject-classroom assignment matrix
- Lesson planning with approval workflow

### 3. Attendance Tracking

- Daily classroom attendance with bulk recording
- Period/subject-level attendance for colleges
- Automated guardian notifications when absent (Celery async)
- Leave request and approval workflow
- Monthly PDF attendance reports

### 4. Gradebook & Assessments

- Configurable grading scales (letter grades + GPA)
- Exam scheduling with venue and invigilator management
- Continuous assessment: homework, quizzes, projects
- Automated report card generation (PDF via ReportLab)
- Class and grade rankings

### 5. Timetable Scheduling

- Drag-and-drop weekly schedule builder
- Conflict detection (teacher double-booking, room clashes)
- School events and holiday calendar

### 6. Communication

- Role-targeted announcements (students / parents / staff)
- Direct messaging between any two users
- Real-time in-app notifications via WebSocket (Django Channels)
- Email (SendGrid), SMS (Twilio), Push (Firebase FCM) channels
- Configurable notification templates per event type

### 7. Fee Management

- Flexible fee structure per grade and category
- Automated invoice generation on schedule
- Online payment gateway integration (Stripe / Khalti / eSewa)
- Scholarship and discount management
- Late fee calculation
- Receipt generation (PDF)

### 8. Reporting & Analytics

- Executive dashboard with KPI cards
- Attendance trend charts (daily, monthly, yearly)
- Grade distribution visualizations
- Fee collection reports with collection rate
- PDF and CSV data exports

---

## 🔗 External Integrations

| System                  | Purpose                              | Status       |
| ----------------------- | ------------------------------------ | ------------ |
| Google Workspace        | SSO + Classroom sync                 | Configurable |
| Microsoft 365           | SSO + Teams integration              | Configurable |
| Zoom                    | Virtual classroom links in timetable | API ready    |
| SendGrid                | Transactional email                  | Active       |
| Twilio                  | SMS notifications                    | Active       |
| Firebase FCM            | Mobile push notifications            | Active       |
| Stripe / Khalti / eSewa | Online fee payment                   | Configurable |
| National Exam Boards    | Result import                        | Via CSV/API  |

---

## 🛠 Technology Stack

| Layer        | Technology                                                      |
| ------------ | --------------------------------------------------------------- |
| Backend      | Python 3.12 · Django 5.2 · Django REST Framework                |
| GraphQL      | Graphene-Django 3.x                                             |
| Auth         | JWT (SimpleJWT) · django-axes (brute-force)                     |
| Task Queue   | Celery 5 · django-celery-beat                                   |
| WebSockets   | Django Channels 4 + channels-redis                              |
| Web Frontend | React 18 · TypeScript · TanStack Query · Zustand · Tailwind CSS |
| Mobile       | React Native · Expo · React Navigation                          |
| Database     | PostgreSQL 16                                                   |
| Cache        | Redis 7                                                         |
| Storage      | AWS S3 / MinIO                                                  |
| Container    | Docker · Kubernetes (EKS / AKS / GKE)                           |
| Monitoring   | Prometheus · Grafana · Sentry                                   |
| CI/CD        | GitHub Actions                                                  |

---

## 📊 Scalability

- **Multi-tenancy**: School-scoped data isolation via FK + middleware
- **Horizontal scaling**: Stateless Django pods behind HPA (2–10 replicas)
- **Async workers**: Celery workers scale independently on task volume
- **Caching**: Redis for sessions, API responses, and computed analytics
- **CDN**: Static/media assets served via CloudFront / CDN
- **Database**: Read replicas supported via `DATABASE_REPLICA_URL`

---

## 🔒 Security

- JWT access tokens (60 min) + rotating refresh tokens (7 days)
- Brute-force protection via django-axes (5 attempts → 30 min lockout)
- Optional 2FA (TOTP via pyotp)
- Tenant isolation enforced at queryset level
- Immutable audit log for all sensitive operations
- HTTPS enforced (HSTS headers via Ingress annotations)
- SQL injection prevention via Django ORM
- XSS protection headers via Nginx
- CSP, CORS, and clickjacking protection

---

## 📄 License

**Proprietary — All rights reserved.**

This software is the exclusive property of EduSphere. No rights are granted
without prior written permission — see the `LICENSE` file for full terms.

---

_Built with ❤️ for educators everywhere._
