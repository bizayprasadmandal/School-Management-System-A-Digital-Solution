# Low-Level Design (LLD) — EduSphere SMS

> **Version:** 2.0  
> **Date:** August 2026  
> **Status:** Current — model schemas and counts re-verified against the code on
> **2026-09-25**  
> **Companion to:** [docs/HLD.md](HLD.md)

---

## 1. Database Schema Design

### 1.1 Entity Relationship Overview

```
                            ┌──────────────┐
                            │    School     │
                            │  (tenant)     │
                            └──────┬───────┘
                                   │ 1:N
                    ┌──────────────┼──────────────────────────┐
                    │              │                           │
              ┌─────▼─────┐ ┌─────▼─────┐ ┌──────────────┐  │
              │   User     │ │ Classroom │ │  FeeCategory  │  │
              │ (all roles)│ │           │ │               │  │
              └─────┬──────┘ └─────┬─────┘ └──────┬───────┘  │
                    │              │               │           │
         ┌──────────┼──────┐      │         ┌─────▼───────┐  │
         │          │      │      │         │FeeStructure  │  │
    ┌────▼───┐ ┌────▼───┐ │ ┌────▼────┐   └──────┬───────┘  │
    │Student │ │Employee│ │ │Enrollment│          │           │
    └────┬───┘ └────┬───┘ │ └────┬────┘   ┌──────▼───────┐  │
         │          │     │      │         │ FeeInvoice    │  │
    ┌────▼────┐     │     │      │         └──────┬───────┘  │
    │Guardian │     │     │      │                │           │
    └─────────┘     │     │      │         ┌──────▼───────┐  │
                    │     │      │         │   Payment     │  │
              ┌─────▼─────▼┐     │         └──────────────┘  │
              │TeacherAssign│    │                            │
              │(Subject×Class)   │                            │
              └──────┬──────┘    │                            │
                     │           │                            │
              ┌──────▼──────┐   │                            │
              │ExamSchedule │   │                            │
              └──────┬──────┘   │                            │
                     │          │                            │
              ┌──────▼──────┐   │                            │
              │   Grade     │   │                            │
              └──────┬──────┘   │                            │
                     │          │                            │
              ┌──────▼──────┐   │                            │
              │ReportCard   │   │                            │
              └─────────────┘   │                            │
                                │                            │
              ┌─────────────┐   │                            │
              │Application  │   │                            │
              │(Admissions) │   │                            │
              └──────┬──────┘   │                            │
                     │          │                            │
              ┌──────▼──────┐   │                            │
              │EntranceAssess│  │                            │
              └─────────────┘   │                            │
```

### 1.2 Core Models — Detailed Schema

#### `auth_service.School` (Tenant Root)

| Field                       | Type                 | Constraints        | Notes                                        |
| --------------------------- | -------------------- | ------------------ | -------------------------------------------- |
| `id`                        | UUID                 | PK                 | Auto-generated                               |
| `name`                      | CharField(255)       | not null           | School display name                          |
| `code`                      | CharField(20)        | unique             | Short code (e.g., "GVS")                     |
| `subdomain`                 | CharField(63)        | unique             | Multi-tenant routing                         |
| `logo`                      | ImageField(100)      | null               | S3 storage                                   |
| `address`                   | TextField            | blank              |                                              |
| `phone`                     | CharField(20)        | blank              |                                              |
| `email`                     | EmailField(254)      | blank              |                                              |
| `website`                   | URLField(200)        | blank              |                                              |
| `timezone`                  | CharField(50)        | default="UTC"      | Schools set `Asia/Kathmandu` in practice     |
| `academic_year_start_month` | PositiveSmallInteger | default=9          | April–March style calendars use 4            |
| `subscription_tier`         | CharField(20)        | default="standard" | Drives plan gating (`core/plan_features.py`) |
| `is_active`                 | BooleanField         | default=True       |                                              |
| `created_at` / `updated_at` | DateTimeField        | auto_now(\_add)    |                                              |

#### `auth_service.User` (Multi-Role)

| Field                             | Type                 | Constraints   | Notes                                                                                                 |
| --------------------------------- | -------------------- | ------------- | ----------------------------------------------------------------------------------------------------- |
| `id`                              | UUID                 | PK            |                                                                                                       |
| `email`                           | EmailField(254)      | unique        | Login identifier                                                                                      |
| `first_name`                      | CharField(100)       | not null      |                                                                                                       |
| `last_name`                       | CharField(100)       | not null      |                                                                                                       |
| `phone`                           | CharField(20)        | blank         |                                                                                                       |
| `avatar`                          | ImageField(100)      | null          | S3 storage                                                                                            |
| `role`                            | CharField(20)        | choices       | `super_admin`, `school_admin`, `teacher`, `student`, `parent`, `accountant`, `librarian`, `counselor` |
| `school`                          | FK → School          | nullable      | null for super_admin                                                                                  |
| `is_active` / `is_staff`          | BooleanField         | default=False |                                                                                                       |
| `email_verified`                  | BooleanField         | default=False | Seeded demo users are set True; False leaves the SPA on /login after auth                             |
| `two_factor_enabled`              | BooleanField         | default=False | TOTP via pyotp                                                                                        |
| `two_factor_secret`               | CharField(32)        | blank         |                                                                                                       |
| `backup_code_failed_attempts`     | PositiveSmallInteger | default=0     | Lockout counter for backup codes                                                                      |
| `backup_code_locked_until`        | DateTimeField        | null          |                                                                                                       |
| `last_login_ip`                   | GenericIPAddress     | null          |                                                                                                       |
| `notify_email` / `_sms` / `_push` | BooleanField         | default=True  | Per-user channel preferences                                                                          |
| `date_joined` / `updated_at`      | DateTimeField        | auto          |                                                                                                       |

The model's `role` choices are the eight above; production data also contains a
legacy `alumni` value (used by the alumni portal accounts), which is why
`scripts/reset_demo_passwords_fast.py` still handles that role.

#### `students.Student`

| Field                                                    | Type              | Constraints  | Notes                                  |
| -------------------------------------------------------- | ----------------- | ------------ | -------------------------------------- |
| `id`                                                     | UUID              | PK           |                                        |
| `user`                                                   | OneToOne → User   | unique       | 1:1 with User                          |
| `school`                                                 | FK → School       | not null     | Tenant FK                              |
| `admission_number`                                       | CharField(30)     | not null     | Unique per school (enforced in `save`) |
| `roll_number`                                            | CharField(20)     | blank        |                                        |
| `date_of_birth`                                          | DateField         | not null     |                                        |
| `gender`                                                 | CharField(1)      | choices      | `M`, `F`, `O`                          |
| `blood_group`                                            | CharField(3)      | blank        |                                        |
| `nationality` / `religion`                               | CharField(50)     | blank        |                                        |
| `address` / `city` / `state` / `country` / `postal_code` | Text/Char(100/20) | blank        | `country` defaults to "Nepal"          |
| `admission_date`                                         | DateField         | not null     |                                        |
| `photo`                                                  | ImageField(100)   | null         |                                        |
| `medical_conditions`                                     | TextField         | blank        | (named `medical_notes` in older docs)  |
| `emergency_contact_name` / `_phone`                      | CharField(100/20) | blank        |                                        |
| `previous_school`                                        | CharField(255)    | blank        |                                        |
| `transfer_certificate`                                   | FileField(100)    | null         |                                        |
| `bio` / `interests` / `learning_goals`                   | TextField         | blank        | Student self-service profile fields    |
| `is_active`                                              | BooleanField      | default=True |                                        |
| `created_at` / `updated_at`                              | DateTimeField     | auto         |                                        |

There is **no `current_classroom` FK on `Student`** — class membership lives in
`students.Enrollment` (`student` + `classroom` + `academic_year`), which is what
the self-service portal and roster views query.

#### `fees.FeeInvoice`

| Field                       | Type              | Constraints | Notes                                                                            |
| --------------------------- | ----------------- | ----------- | -------------------------------------------------------------------------------- |
| `id`                        | UUID              | PK          |                                                                                  |
| `invoice_number`            | CharField(30)     | unique      | Auto-generated; includes the school code so numbers never collide across tenants |
| `student`                   | FK → Student      | not null    | Tenant comes through the student (there is **no** `school` FK on the invoice)    |
| `academic_year`             | FK → AcademicYear | not null    |                                                                                  |
| `fee_structure`             | FK → FeeStructure | not null    | Defines the base amount                                                          |
| `due_date`                  | DateField         | not null    |                                                                                  |
| `base_amount`               | DecimalField      | not null    | From the fee structure                                                           |
| `discount_amount`           | DecimalField      | default=0   | Concessions/scholarships                                                         |
| `late_fee`                  | DecimalField      | default=0   | Applied by `process_installments` / late-fee rules                               |
| `total_amount`              | DecimalField      | not null    | `base − discount + late_fee`                                                     |
| `paid_amount`               | DecimalField      | default=0   | Running total                                                                    |
| `status`                    | CharField(15)     | choices     | `draft`, `unpaid`, `partial`, `paid`, `overdue`, `waived`, `cancelled`           |
| `notes`                     | TextField         | blank       |                                                                                  |
| `created_by`                | FK → User         | nullable    | Staff member who generated it                                                    |
| `created_at` / `updated_at` | DateTimeField     | auto        |                                                                                  |

#### `admissions.Application`

| Field                                                    | Type                  | Constraints | Notes                                                      |
| -------------------------------------------------------- | --------------------- | ----------- | ---------------------------------------------------------- |
| `id`                                                     | UUID                  | PK          |                                                            |
| `school`                                                 | FK → School           | not null    | Tenant FK                                                  |
| `intake`                                                 | FK → EnrollmentIntake | not null    | Application round                                          |
| `application_number`                                     | CharField(50)         | unique      | `APP-<YYYYMM>-<6 uppercase hex>`, e.g. `APP-202609-4F2A9C` |
| `status`                                                 | CharField(20)         | choices     | State machine (see §2.1)                                   |
| `first_name` / `middle_name` / `last_name`               | CharField(100)        | —           |                                                            |
| `date_of_birth`                                          | DateField             | not null    |                                                            |
| `gender`                                                 | CharField(10)         | choices     |                                                            |
| `nationality`                                            | CharField(100)        | blank       |                                                            |
| `email`                                                  | EmailField(254)       | not null    |                                                            |
| `phone`                                                  | CharField(20)         | not null    |                                                            |
| `address` / `city` / `state` / `postal_code`             | Text/Char(100/20)     | blank       |                                                            |
| `previous_school` / `previous_grade`                     | Char(200/20)          | blank       |                                                            |
| `applying_for_grade`                                     | CharField(20)         | not null    | Free-text grade name                                       |
| `gpa`                                                    | DecimalField          | null        | Optional self-reported GPA                                 |
| `guardian_name`                                          | CharField(200)        | not null    |                                                            |
| `guardian_phone`                                         | CharField(20)         | not null    |                                                            |
| `guardian_email`                                         | EmailField(254)       | not null    |                                                            |
| `guardian_relation`                                      | CharField(50)         | blank       | `father`, `mother`, `guardian`, `other`                    |
| `source`                                                 | CharField(50)         | blank       | Marketing attribution                                      |
| `submitted_at`                                           | DateTimeField         | null        | Set on the draft → submitted transition                    |
| `reviewed_by` / `review_notes`                           | FK → User / TextField | null        | Admin review                                               |
| `tour_date` / `toured_at`                                | Date/DateTimeField    | null        | Campus tour tracking                                       |
| `offer_sent_at` / `offer_deadline` / `offer_accepted_at` | DateTime/Date         | null        | Offer lifecycle                                            |
| `linked_student`                                         | FK → Student          | null        | Set when the applicant is enrolled                         |
| `created_at` / `updated_at`                              | DateTimeField         | auto        |                                                            |

The 40-model `admissions` app also carries the funnel/reporting models
(`AdmissionFunnelSnapshot`, `AdmissionDecision`, `AdmissionDocumentChecklist`,
`AdmissionReminder`, …) built on top of this core record.

### 1.3 Key Relationships

| Relationship                           | Type | FK Field                  | On Delete |
| -------------------------------------- | ---- | ------------------------- | --------- |
| School → User                          | 1:N  | `user.school`             | CASCADE   |
| School → Student                       | 1:N  | `student.school`          | CASCADE   |
| Student → User                         | 1:1  | `student.user`            | CASCADE   |
| Student → Guardian                     | M:N  | `StudentGuardian`         | CASCADE   |
| Student → Enrollment                   | 1:N  | `enrollment.student`      | CASCADE   |
| Enrollment → Classroom                 | N:1  | `enrollment.classroom`    | PROTECT   |
| Classroom → AcademicYear               | N:1  | `classroom.academic_year` | PROTECT   |
| TeacherAssignment → Subject            | N:1  | assignment.subject        | CASCADE   |
| TeacherAssignment → Classroom          | N:1  | assignment.classroom      | CASCADE   |
| Exam → ExamSchedule                    | 1:N  | schedule.exam             | CASCADE   |
| ExamSchedule → Grade                   | 1:N  | grade.exam_schedule       | CASCADE   |
| FeeStructure → FeeInvoice              | 1:N  | invoice.fee_structure     | CASCADE   |
| FeeInvoice → Payment                   | 1:N  | payment.invoice           | CASCADE   |
| Application → EntranceAssessment       | 1:1  | assessment.application    | CASCADE   |
| Application → ApplicationTimelineEvent | 1:N  | event.application         | CASCADE   |

---

## 2. State Machines

### 2.1 Admissions Application State Machine

Defined as `Application.VALID_TRANSITIONS` in `services/admissions/models.py`
(`Status` = `draft`, `submitted`, `under_review`, `shortlisted`, `accepted`,
`rejected`, `waitlisted`, `enrolled`, `cancelled`):

```
   ┌──────────┐  POST /public/apply/   ┌────────────┐
   │  draft   │───────────────────────▶│ submitted  │
   └────┬─────┘  (public form saves    └─────┬──────┘
        │         straight to submitted)     │
        │                                     ▼
        │                            ┌───────────────┐
        │                            │ under_review  │
        │                            └──┬──┬──┬──────┘
        │                               │  │  │
        │        ┌──────────────────────┘  │  └────────────┐
        │        ▼                         ▼               ▼
        │  ┌────────────┐          ┌────────────┐   ┌────────────┐
        │  │shortlisted │          │ waitlisted │   │  rejected  │
        │  └─────┬──────┘          └──────┬─────┘   └────────────┘
        │        │        ┌───────────────┘
        │        ▼        ▼
        │  ┌────────────────┐
        │  │    accepted    │
        │  └────────┬───────┘
        ▼           ▼
   ┌──────────┐  ┌────────────┐
   │cancelled │  │  enrolled  │
   └──────────┘  └────────────┘
```

| From                                  | Allowed next states                                  |
| ------------------------------------- | ---------------------------------------------------- |
| `draft`                               | `submitted`, `cancelled`                             |
| `submitted`                           | `under_review`, `rejected`, `cancelled`              |
| `under_review`                        | `shortlisted`, `rejected`, `waitlisted`, `cancelled` |
| `shortlisted`                         | `accepted`, `rejected`, `cancelled`                  |
| `waitlisted`                          | `accepted`, `rejected`, `cancelled`                  |
| `accepted`                            | `enrolled`, `cancelled`                              |
| `rejected` / `enrolled` / `cancelled` | terminal                                             |

**Side effects on transition:**

- Submission: generate `application_number`, stamp `submitted_at`, write an
  `ApplicationTimelineEvent`, send the applicant a confirmation email
  (best-effort — a mail failure is logged, never rolled back into the response)
- Offer/pre-offer states: set `offer_sent_at` / `offer_deadline`, notify the
  applicant; `expire_overdue_offers` (Celery beat, daily 06:00) closes expired offers
- `accepted → enrolled`: create the student + guardian accounts, link them via
  `linked_student`, send the welcome email
- `rejected`: send the rejection email

### 2.2 Fee Payment State Machine

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  draft    │────▶│  unpaid   │────▶│  partial  │
└──────────┘     └──────────┘     └──────────┘
                      │                │
                      │                ▼
                      │          ┌──────────┐
                      └─────────▶│   paid    │
                                 └──────────┘
                      │
                      ▼
                ┌──────────┐
                │ overdue   │ (Celery beat: daily check)
                └──────────┘
                      │
                      ▼
                ┌──────────┐
                │  waived   │ (Admin action)
                └──────────┘
```

### 2.3 Grade Change Workflow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ proposed  │────▶│ approved  │────▶│ published │
└──────────┘     └──────────┘     └──────────┘
       │
       ▼
 ┌──────────┐
 │ rejected  │
 └──────────┘
```

---

## 3. API Contract Design

### 3.1 REST API Conventions

| Convention         | Implementation                                                                     |
| ------------------ | ---------------------------------------------------------------------------------- |
| **Base URL**       | `/api/v1/<service>/`                                                               |
| **List**           | `GET /<service>/` → paginated `{ count, next, previous, results }`                 |
| **Detail**         | `GET /<service>/{id}/` → single object                                             |
| **Create**         | `POST /<service>/` → 201 + object                                                  |
| **Update**         | `PUT/PATCH /<service>/{id}/` → 200 + object                                        |
| **Delete**         | `DELETE /<service>/{id}/` → 204                                                    |
| **Custom actions** | `POST /<service>/{id}/<action>/` → varies                                          |
| **Filtering**      | Query params: `?search=`, `?status=`, `?page=`, `?page_size=`                      |
| **Pagination**     | Page-number based, default 25 / max 200 per page                                   |
| **Auth**           | `Authorization: Bearer <access>` (tenant-aware JWT); login public                  |
| **Throttling**     | anon 50/h · user 6 000/h · login 10/min · 2FA 5/min (429 + `Retry-After`)          |
| **Self-service**   | `<module>/…/children/` guardian-scoped routes; students self-scope on 4 viewsets   |
| **Docs**           | `/api/schema/` (OpenAPI 3), `/api/docs/` (Swagger UI), `/api/redoc/`               |
| **Error format**   | `{ "detail": "...", "status_code": 400 }` or field errors `{ "field": ["error"] }` |

### 3.2 Key API Endpoints

#### Authentication

```
POST   /auth/login/                    → { access, refresh, user }
POST   /auth/token/refresh/            → { access }
POST   /auth/password-reset/           → { detail }
POST   /auth/password-reset/confirm/   → { detail }
POST   /auth/verify-2fa/               → { access, refresh, user }
GET    /auth/me/                       → { user profile }
POST   /auth/logout/                   → { detail }
```

#### Students

```
GET    /students/                      → paginated list
POST   /students/                      → create student
GET    /students/{id}/                 → student detail
PATCH  /students/{id}/                 → partial update
DELETE /students/{id}/                 → soft delete
GET    /students/{id}/attendance-summary/ → attendance stats
POST   /students/promote/              → bulk promotion
POST   /students/import-csv/           → CSV bulk import
```

#### Attendance

```
GET    /attendance/                    → paginated records
POST   /attendance/bulk-record/        → bulk daily recording
GET    /attendance/classroom-summary/  → classroom stats
POST   /attendance/import-csv/         → CSV bulk import
GET    /attendance/student-report/     → per-student report
POST   /attendance/leaves/             → create leave request
POST   /attendance/leaves/{id}/approve/ → approve leave
```

#### Gradebook

```
GET    /gradebook/exams/               → paginated exams
POST   /gradebook/exams/               → create exam
GET    /gradebook/exams/{id}/leaderboard/ → top students
POST   /gradebook/exams/{id}/generate-report-cards/ → async PDF
GET    /gradebook/grades/              → paginated grades
POST   /gradebook/grades/bulk/         → bulk grade entry
POST   /gradebook/grades/import-csv/   → CSV import
GET    /gradebook/grades/history/      → grade change audit
POST   /gradebook/report-cards/{id}/publish/ → publish report card
```

#### Fees

```
GET    /fees/invoices/                 → paginated invoices
POST   /fees/invoices/bulk-generate/   → bulk creation
GET    /fees/invoices/{id}/            → invoice detail
POST   /fees/payments/                 → record payment
POST   /fees/payments/stripe/          → Stripe checkout session
POST   /fees/payments/khalti/          → Khalti initiation
POST   /fees/payments/esewa/           → eSewa initiation
POST   /fees/payments/stripe/webhook/  → Stripe callback
POST   /fees/payments/khalti/verify/   → Khalti verify
POST   /fees/payments/refund/          → refund payment
GET    /fees/scholarships/             → list scholarships
POST   /fees/scholarships/             → create scholarship
```

#### Admissions (Admin)

```
GET    /admissions/intakes/            → list intakes
POST   /admissions/intakes/            → create intake
GET    /admissions/applications/       → paginated applications
GET    /admissions/applications/{id}/  → application detail
PATCH  /admissions/applications/{id}/  → update status (state machine)
POST   /admissions/applications/{id}/enroll/ → enroll student
```

#### Admissions (Public — No Auth)

```
POST   /admissions/public/apply/       → submit application (201 + application_number)
GET    /admissions/public/status/{application_number}/ → check status + timeline
GET    /admissions/public/intakes/     → list open intakes (unpaginated)
```

#### Communication

```
GET    /communication/announcements/   → list announcements
POST   /communication/announcements/   → create announcement
GET    /communication/notifications/   → paginated notifications
GET    /communication/notifications/unread-count/ → badge count
POST   /communication/notifications/mark-all-read/ → mark all
GET    /communication/messages/        → direct messages
POST   /communication/messages/        → send message
```

#### Reporting

```
GET    /reporting/dashboard-stats/     → KPI summary
GET    /reporting/at-risk-students/    → at-risk list
GET    /reporting/enrollment-funnel/   → admissions funnel
GET    /reporting/fee-forecast/        → 90-day projection
GET    /reporting/export/students-csv/ → CSV download
GET    /reporting/export/attendance-pdf/ → PDF download
```

### 3.3 WebSocket Protocols

#### Notifications Channel

```
Connection: ws://host/ws/notifications/?token=<jwt>
Protocol: Sec-WebSocket-Protocol: jwt

Server → Client:
  { "type": "notification", "notification": { "id", "title", "body", "created_at" } }
  { "type": "unread_count", "count": 7 }

Client → Server:
  { "type": "mark_read", "notification_id": "uuid" }
```

#### Chat Channel

```
Connection: ws://host/ws/chat/{recipient_id}/?token=<jwt>

Client → Server:
  { "type": "message", "content": "Hello" }
  { "type": "typing", "is_typing": true }
  { "type": "read_receipt", "message_ids": ["uuid"] }

Server → Client:
  { "type": "chat_message", "message": { "id", "content", "sender_id", "sent_at" } }
  { "type": "typing_indicator", "user_id": "uuid", "is_typing": true }
  { "type": "read_receipt", "reader_id": "uuid", "message_ids": [...], "read_at": "..." }
```

---

## 4. Sequence Diagrams

### 4.1 Student Login with 2FA

```
Browser          Backend           Redis          Celery
  │                │                │               │
  │──POST /auth/login/──▶│                │               │
  │                │──validate creds──▶│               │
  │                │──check axes lock──▶│               │
  │                │◀──OK──────────────│               │
  │                │──generate TOTP──▶│               │
  │                │──send 2FA code───│──────────────▶│
  │                │                   │          (email)
  │◀──{ challenge }│                │               │
  │                │                │               │
  │──POST /auth/verify-2fa/──▶│                │               │
  │                │──validate TOTP──▶│               │
  │                │──mint JWT tokens──▶│               │
  │◀──{ access, refresh, user }│                │               │
  │                │                │               │
  │──GET /students/?token=...──▶│                │               │
  │                │──JWT verify──▶│               │
  │                │──scope by school│               │
  │◀──paginated list│                │               │
```

### 4.2 Fee Payment via Khalti

```
Student          Backend          Khalti API       Celery
  │                │                │               │
  │──POST /fees/payments/khalti/──▶│                │               │
  │                │──create Payment(pending)──▶│               │
  │                │──initiate Khalti──▶│               │
  │                │◀──payment_url──────────│               │
  │◀──{ khalti_url }│                │               │
  │                │                │               │
  │──(redirect to Khalti)──▶│                │               │
  │──(user completes payment)──▶│                │               │
  │                │                │               │
  │                │◀──POST /webhook/khalti/──────│               │
  │                │──verify with Khalti──▶│               │
  │                │◀──confirmation──────────│               │
  │                │──update Payment(complete)──▶│               │
  │                │──update Invoice status──▶│               │
  │                │──send receipt email──────────────▶│
  │                │──send notification──▶│──────────────▶│
  │                │                │          (email+push)
```

### 4.3 Public Application Submission

```
Applicant        Backend          PostgreSQL       Celery
  │                │                │               │
  │──POST /admissions/public/apply/──▶│                │               │
  │                │──validate serializer──▶│               │
  │                │──generate application_number (APP-YYYYMM-XXXXXX)│               │
  │                │──create Application(submitted)──▶│               │
  │                │──create TimelineEvent──▶│               │
  │◀──{ application_number, status, intake_name }│               │
  │                │                │               │
  │──GET /admissions/public/status/APP-.../──▶│                │
  │                │──query by application_number──▶│               │
  │◀──{ status, details }│                │               │
```

### 4.4 Attendance Recording with Notification

```
Teacher          Backend          PostgreSQL       Celery          Parent
  │                │                │               │               │
  │──POST /attendance/bulk-record/──▶│                │               │
  │                │──validate records──▶│               │               │
  │                │──bulk create AttendanceRecord──▶│               │
  │                │──fire signal (post_save)──▶│               │
  │                │                │          dispatch Celery task
  │◀──{ recorded: 35 }│                │               │               │
  │                │                │               │               │
  │                │                │          ┌────▼────┐          │
  │                │                │          │ check if │          │
  │                │                │          │ absent   │          │
  │                │                │          └────┬────┘          │
  │                │                │               │               │
  │                │                │          send email──▶│       │
  │                │                │          send SMS──▶│         │
  │                │                │          send push──▶│        │
```

---

## 5. Error Handling Strategy

### 5.1 Backend Error Response Format

```json
// Validation error (400)
{
  "email": ["A user with this email already exists."],
  "status_code": 400
}

// Permission denied (403)
{
  "detail": "You do not have permission to perform this action.",
  "status_code": 403
}

// Not found (404)
{
  "detail": "Not found.",
  "status_code": 404
}

// Rate limited (429)
{
  "detail": "Request was throttled. Please try again in 30 seconds.",
  "status_code": 429,
  "retry_after": 30
}

// Server error (500) — forwarded to Sentry
{
  "detail": "Internal server error.",
  "status_code": 500
}
```

### 5.2 Error Handling Layers

```
Request
  │
  ├─▶ Nginx          → 502 (backend down), 413 (payload too large)
  │
  ├─▶ Middleware      → CORS (403), Axes (429 lockout), CSRF (403)
  │
  ├─▶ DRF Exception  → Validation (400), Permission (403), Not Found (404)
  │   Handler        → Throttle (429)
  │
  ├─▶ ViewSet        → Business logic errors (custom exceptions)
  │
  ├─▶ Serializer     → Field validation, cross-field validation
  │
  └─▶ Sentry         → All 500s captured with full context
```

### 5.3 Celery Task Error Handling

```python
# Pattern: exponential backoff with max retries
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # seconds
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
)
def send_notification(self, user_id, message):
    try:
        # ... send logic
    except TwilioException as exc:
        self.retry(exc=exc)
    except Exception as exc:
        # Log to Sentry via task_failure signal
        logger.error("notification_failed", extra={"user_id": user_id})
        raise
```

---

## 6. Caching Design

### 6.1 Cache Keys Convention

```
sms:{school_id}:{module}:{resource}:{id}

Examples:
  sms:school123:reporting:dashboard_stats
  sms:school123:students:list:page_1
  sms:school123:fees:invoice_status:{invoice_id}
  sms:school123:notifications:unread_count:{user_id}
```

### 6.2 Cache Invalidation Strategy

| Event               | Invalidates                                   | Method                           |
| ------------------- | --------------------------------------------- | -------------------------------- |
| Attendance recorded | Dashboard stats, student attendance summary   | Signal → Celery task             |
| Payment received    | Invoice status, dashboard stats, fee forecast | Signal → Celery task             |
| Grade published     | Report card cache, dashboard stats            | Post-publish signal              |
| User login          | Session cache                                 | Django session framework         |
| Notification sent   | Unread count                                  | WebSocket push (no cache needed) |

### 6.3 React Query Cache Configuration

```typescript
// Default query client config
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000, // 1 min — data is fresh for 1 min
      gcTime: 5 * 60_000, // 5 min — garbage collect after 5 min
      retry: 2, // Retry failed requests twice
      refetchOnWindowFocus: true, // Refetch when tab focused
    },
    mutations: {
      onSuccess: () => {
        // Invalidate related queries after mutation
        queryClient.invalidateQueries();
      },
    },
  },
});
```

---

## 7. Message Queue Design

### 7.1 Queue Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Celery Beat (Scheduler)             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Daily backup  │  │ Offer expiry │  │ Low backup│ │
│  │ (03:00 AM)    │  │ (hourly)     │  │ codes     │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
└─────────┼─────────────────┼─────────────────┼───────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────┐
│                   Redis (Message Broker)               │
│                                                         │
│  ┌──────────────┐  ┌────────────────┐  ┌───────────┐ │
│  │   default     │  │ notifications  │  │  reports   │ │
│  │   queue       │  │   queue        │  │  queue     │ │
│  └──────┬───────┘  └──────┬─────────┘  └─────┬─────┘ │
└─────────┼─────────────────┼───────────────────┼───────┘
          │                 │                   │
          ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────┐
│              Celery Workers (2–8 pods)                 │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Worker Pool: 4 threads per worker               │ │
│  │  Prefetch: 1 task per thread (fair scheduling)   │ │
│  │  Timeout: 300s hard / 120s soft                  │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### 7.2 Task Categories

| Queue             | Tasks                                                   | Priority |
| ----------------- | ------------------------------------------------------- | -------- |
| **default**       | Bulk invoice generation, report card PDF, grade imports | Normal   |
| **notifications** | Email (SendGrid), SMS (Twilio), push (FCM), WebSocket   | High     |
| **reports**       | CSV exports, PDF generation, analytics computation      | Normal   |

### 7.3 Scheduled Tasks (Celery Beat)

| Task                                  | Schedule      | Purpose                                    |
| ------------------------------------- | ------------- | ------------------------------------------ |
| `cleanup-expired-verification-tokens` | Every 6 hours | Purge old email verify tokens              |
| `notify-low-backup-codes`             | Daily 9 AM    | Alert admins when 2FA backup codes are low |
| `create_database_backup`              | Daily 3 AM    | pg_dump + gzip + S3 mirror                 |
| `expire-offer-deadlines`              | Hourly        | Auto-reject expired admission offers       |
| `check-overdue-invoices`              | Daily 6 AM    | Mark unpaid invoices as overdue            |
| `send-fee-reminders`                  | Daily 8 AM    | Email reminders for upcoming due dates     |

### 7.4 Task Monitoring

```
Celery Flower (port 5555)
  │
  ├─▶ Task success/failure rates
  ├─▶ Worker memory/CPU usage
  ├─▶ Queue depth per queue
  ├─▶ Task execution time histogram
  └─▶ Active/scheduled/reserved tasks

Prometheus Metrics (via Celery exporter)
  │
  ├─▶ celery_task_sent_total
  ├─▶ celery_task_runtime_seconds
  ├─▶ celery_worker_total
  └─▶ celery_queue_length
```

---

## 8. PDF Generation Design

### 8.1 Report Card Generation Flow

```
Admin clicks "Generate Report Cards"
  │
  ▼
POST /gradebook/exams/{id}/generate-report-cards/
  │
  ▼
Celery task queued (reports queue)
  │
  ▼
For each student in exam:
  ├── Query grades, attendance summary
  ├── Calculate GPA, rank
  ├── Generate PDF via ReportLab
  │     ├── School header (logo, name, address)
  │     ├── Student info + class
  │     ├── Grade table (subject, marks, grade, GPA)
  │     ├── Attendance summary
  │     ├── Teacher remarks
  │     └── Footer (school stamp, date)
  ├── Store PDF in S3/MinIO
  └── Update ReportCard record (status: generated)
  │
  ▼
WebSocket notification → Admin: "Report cards ready"
Email → Parents: "Report card available for download"
```

### 8.2 PDF Template Structure (ReportLab)

```python
class ReportCardPDF:
    def build(self):
        self._header()          # School logo + name + address
        self._student_info()    # Name, class, admission number, term
        self._grade_table()     # Subject | Midterm | Final | Grade | GPA
        self._attendance()      # Present | Absent | Late | Percentage
        self._rank()            # Class rank, grade rank
        self._remarks()         # Teacher + principal remarks
        self._footer()          # Date, signature lines, school stamp
```

---

## 9. Notification System Design

### 9.1 Multi-Channel Dispatch

```
┌──────────────┐
│   Event       │  (e.g., attendance_absent, payment_received)
│   Trigger     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Notification  │  Matches event_type → NotificationTemplate
│ Template      │  Resolves recipient (student, parent, teacher)
└──────┬───────┘
       │
       ├─────────────────┬─────────────────┬─────────────────┐
       ▼                 ▼                 ▼                 ▼
  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ In-App   │    │  Email   │    │   SMS    │    │   Push   │
  │(WebSocket│    │(SendGrid)│    │ (Twilio) │    │  (FCM)   │
  │ + DB)    │    │          │    │          │    │          │
  └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### 9.2 Notification Template System

```python
# Template variable resolution
TEMPLATE_VARIABLES = {
    "student_name": lambda ctx: ctx["student"].full_name,
    "parent_name": lambda ctx: ctx["guardian"].full_name,
    "amount": lambda ctx: f"NPR {ctx['invoice'].amount:,.2f}",
    "date": lambda ctx: ctx["date"].strftime("%B %d, %Y"),
    "school_name": lambda ctx: ctx["school"].name,
    "tracking_id": lambda ctx: ctx["application"].tracking_id,
}

# Template rendering
def render_template(template: str, context: dict) -> str:
    for var, resolver in TEMPLATE_VARIABLES.items():
        if var in context:
            template = template.replace(f"{{{{{var}}}}}", resolver(context))
    return template
```

---

## 10. Security Implementation Details

### 10.1 JWT Token Lifecycle

```
Login
  │
  ├─▶ Access token (60 min) — stored in memory (httpOnly cookie or memory)
  │     Contains: user_id, school_id, role, exp
  │     Signed: HS256 with SECRET_KEY
  │
  └─▶ Refresh token (7 days) — stored in SecureStore (mobile) or httpOnly cookie
        Contains: user_id, jti (unique ID), exp
        Rotation: new refresh token on each use
        Blacklisting: on logout, jti added to Redis blacklist
```

### 10.2 RBAC Permission Matrix

| Action             | Super Admin | School Admin | Teacher        | Accountant | Student | Parent   |
| ------------------ | ----------- | ------------ | -------------- | ---------- | ------- | -------- |
| View all schools   | ✅          | ❌           | ❌             | ❌         | ❌      | ❌       |
| CRUD students      | ✅          | ✅           | 👁 own         | ❌         | 👁 self | 👁 child |
| Record attendance  | ✅          | ✅           | ✅ own class   | ❌         | ❌      | ❌       |
| Enter grades       | ✅          | ✅           | ✅ own subject | ❌         | ❌      | ❌       |
| Manage fees        | ✅          | ✅           | ❌             | ✅ full    | 👁 own  | 💳 pay   |
| View reports       | ✅          | ✅           | 👁 own         | ✅ fee     | 👁 self | 👁 child |
| Manage HR          | ✅          | ✅           | ❌             | ❌         | ❌      | ❌       |
| Access admin panel | ✅          | ✅           | ❌             | ❌         | ❌      | ❌       |
| Process payments   | ✅          | ✅           | ❌             | ✅         | ❌      | ✅ self  |

### 10.3 Tenant Isolation Enforcement

```python
# Middleware: sets school context from X-School-ID header
class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        school_id = request.headers.get("X-School-ID")
        if school_id and request.user.is_authenticated:
            if request.user.role == "super_admin":
                request.school = School.objects.get(id=school_id)
            elif str(request.user.school_id) == school_id:
                request.school = request.user.school
            else:
                raise PermissionDenied("Cross-tenant access denied")
        return self.get_response(request)

# ViewSet: automatic school scoping
class StudentViewSet(ModelViewSet):
    def get_queryset(self):
        return Student.objects.filter(
            school=self.request.user.school
        )
```

---

## 11. Frontend Component Architecture

### 11.1 Page Module Structure

```
pages/
├── admin/                    # School admin pages
│   ├── DashboardPage.tsx     # KPI cards, charts
│   ├── StudentsPage.tsx      # Student CRUD + search
│   ├── TeachersPage.tsx      # Teacher management
│   ├── ClassroomsPage.tsx    # Classroom assignment
│   ├── ExamsPage.tsx         # Exam scheduling
│   ├── AdmissionsPage.tsx    # Application pipeline
│   ├── ReportsPage.tsx       # Analytics + exports
│   └── SettingsPage.tsx      # School settings
├── teacher/                  # Teacher pages
│   ├── TeacherDashboard.tsx  # My classes, upcoming
│   ├── AttendancePage.tsx    # Bulk attendance
│   ├── GradebookPage.tsx     # Grade entry
│   └── LessonPlansPage.tsx   # Lesson plans
├── student/                  # Student pages
│   ├── StudentDashboard.tsx  # My grades, attendance
│   ├── AttendancePage.tsx    # My attendance history
│   └── FeesPage.tsx          # My invoices
├── parent/                   # Parent pages
│   ├── ParentDashboard.tsx   # Children overview
│   ├── ChildrenPage.tsx      # Child detail
│   └── FeesPage.tsx          # Pay fees
├── public/                   # Unauthenticated
│   ├── PublicApplyPage.tsx   # Application form
│   └── PublicStatusPage.tsx  # Status tracker
├── auth/                     # Authentication
│   ├── LoginPage.tsx         # Email + password
│   ├── Verify2FALoginPage.tsx # TOTP / backup code
│   └── Setup2FAPage.tsx      # 2FA enrollment
└── shared/                   # Cross-role pages
    ├── ProfilePage.tsx        # User profile
    ├── NotificationsPage.tsx  # Notification center
    └── ChatPage.tsx           # Direct messaging
```

### 11.2 Data Flow Pattern

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Page       │────▶│ React Query  │────▶│ Axios Client│
│  Component   │◀────│  Hook        │◀────│ (apiClient) │
│              │     │  useQuery()  │     │             │
│  useState()  │     │  useMutation()│    │ Interceptor │
│  for UI only │     │  for server  │     │ adds JWT    │
└─────────────┘     │  state       │     └──────┬──────┘
                    └─────────────┘            │
                                               ▼
                                        ┌─────────────┐
                                        │  Django API  │
                                        │  /api/v1/*   │
                                        └─────────────┘
```

---

## Appendix: File Count Summary

Counts re-verified against the code on **2026-09-25** (`apps.get_models()`, the
URL resolver, and file counts):

| Category                   | Count                                                |
| -------------------------- | ---------------------------------------------------- |
| Django service modules     | 23 (+ `core`)                                        |
| Django models (classes)    | 938 (937 defined in `services/*/models.py`)          |
| Django migrations          | 116 files (every service app has an `0001_initial`)  |
| DRF ViewSets               | 945                                                  |
| DRF Serializers            | 975                                                  |
| URL router registrations   | 941                                                  |
| URL patterns under `/api/` | 4 407 (2 202 documented paths in the OpenAPI schema) |
| Celery task definitions    | 38 (17 on the Beat schedule)                         |
| Celery queues              | `default`, `notifications`, `reports`                |
| Backend tests              | 974 pytest tests in 59 files                         |
| React pages / routes       | 177 page modules, 171 routes in `App.tsx`            |
| React shared components    | 45 `.tsx` under `src/components`                     |
| Jest unit tests            | 46 test files                                        |
| Playwright e2e tests       | 11 spec files in `frontend/web/e2e`                  |
| k6 load test scripts       | 5                                                    |
| WebSocket consumers        | 3 (`Chat`, `Notification`, `AttendanceLive`)         |
| React Native screens       | 40 `.tsx` files                                      |
