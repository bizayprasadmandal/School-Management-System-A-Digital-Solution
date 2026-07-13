import http from 'k6/http';
import { check, sleep } from 'k6';

/**
 * Smoke Test — Rapid CI Validation
 *
 * Runs a single iteration across all critical API endpoints to validate that
 * the backend is healthy and responding correctly.  Designed for CI pipelines
 * where full load tests would take too long.
 *
 * Usage:
 *   k6 run smoke.js
 *   k6 run -e BASE_URL=https://staging.example.com/api/v1 smoke.js
 *
 * Exit code: 0 if all checks pass, non-zero if any check fails.
 * Perfect for `continue-on-error: false` CI steps.
 */

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000/api/v1';

// ── Test thresholds ─────────────────────────────────────────────────────────

export const options = {
  vus: 1,
  iterations: 1,
  thresholds: {
    http_req_duration: ['max<10000'],  // Any single request must complete in < 10s
    http_req_failed:   ['rate<1.0'],   // Accept any HTTP failure rate (checks handle business logic)
    checks:            ['rate>0.99'],  // ALL assertions must pass — this is the real CI gate
  },
};

// ── Setup: Authenticate admin and teacher ───────────────────────────────────

export function setup() {
  // Admin login
  const adminLogin = http.post(`${BASE_URL}/auth/login/`, {
    email: 'admin@demo.edusphere.school',
    password: 'Admin@1234',
  });

  const adminOk = adminLogin.status === 200;
  const adminToken = adminOk ? adminLogin.json('access') : null;

  // Teacher login
  const teacherLogin = http.post(`${BASE_URL}/auth/login/`, {
    email: 'teacher@demo.edusphere.school',
    password: 'Teacher@1234',
  });

  const teacherOk = teacherLogin.status === 200;
  const teacherToken = teacherOk ? teacherLogin.json('access') : null;

  // Student login
  const studentLogin = http.post(`${BASE_URL}/auth/login/`, {
    email: 'student@demo.edusphere.school',
    password: 'Student@1234',
  });

  const studentOk = studentLogin.status === 200;
  const studentToken = studentOk ? studentLogin.json('access') : null;

  return {
    auth_ok: adminOk && teacherOk && studentOk,
    admin_headers: { Authorization: `Bearer ${adminToken}`, 'Content-Type': 'application/json' },
    teacher_headers: { Authorization: `Bearer ${teacherToken}`, 'Content-Type': 'application/json' },
    student_headers: { Authorization: `Bearer ${studentToken}`, 'Content-Type': 'application/json' },
  };
}

// ── Smoke test: one pass through all critical endpoints ─────────────────────

export default function (data) {
  if (!data.auth_ok) {
    console.error('❌  Auth: One or more demo accounts failed to log in');
    // The checks below will find data.auth_ok is falsy, but let's hard-fail
    // to make it obvious in CI logs.
    throw new Error('Setup login failed — demo data may not be seeded');
  }

  const { admin_headers, teacher_headers, student_headers } = data;
  const base = BASE_URL;

  // ══════════════════════════════════════════════════════════════════════════
  //  1. AUTH
  // ══════════════════════════════════════════════════════════════════════════

  // Token refresh
  const refreshRes = http.post(`${base}/auth/token/refresh/`, {
    refresh: '', // Empty token — expects 400, not 401 or 500
  });
  check(refreshRes, {
    'auth/refresh returns 400 for empty token': (r) => r.status === 400,
  });

  // Profile (admin) — verify email_verified field is present
  const profileRes = http.get(`${base}/auth/me/`, { headers: admin_headers });
  check(profileRes, {
    'auth/me returns profile': (r) => r.status === 200 && r.json('email') !== undefined,
    'auth/me includes email_verified': (r) => r.json('email_verified') !== undefined,
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  1b. EMAIL VERIFICATION
  //     Validates the email verification endpoints are wired correctly.
  //     Full happy path requires an unverified user; demo accounts are
  //     pre-verified, so we test the error cases which still exercise
  //     the full request cycle (auth → serialize → validate → respond).
  // ══════════════════════════════════════════════════════════════════════════

  // Send verification for an already-verified user → expects 400
  const sendVerifRes = http.post(`${base}/auth/send-verification/`, {
    email: 'admin@demo.edusphere.school',
  }, { headers: admin_headers });
  check(sendVerifRes, {
    'auth/send-verification returns 400 (already verified)': (r) => r.status === 400,
    'auth/send-verification body mentions verified': (r) => {
      const body = r.json();
      return JSON.stringify(body).toLowerCase().includes('verified');
    },
  });

  // Verify an invalid/expired token → expects 400
  const confirmVerifRes = http.post(`${base}/auth/verify-email/`, {
    token: 'invalid-token-that-does-not-exist-in-the-database',
  });
  check(confirmVerifRes, {
    'auth/verify-email returns 400 for invalid token': (r) => r.status === 400,
    'auth/verify-email body mentions invalid or used': (r) => {
      const body = JSON.stringify(r.json()).toLowerCase();
      return body.includes('invalid') || body.includes('used') || body.includes('expired');
    },
  });

  // Verify that unauthenticated access to send-verification is rejected
  const unauthVerifRes = http.post(`${base}/auth/send-verification/`, {
    email: 'admin@demo.edusphere.school',
  });
  check(unauthVerifRes, {
    'auth/send-verification returns 401 when unauthenticated': (r) => r.status === 401,
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  2. STUDENTS (admin)
  // ══════════════════════════════════════════════════════════════════════════

  const studentsRes = http.get(`${base}/students/?page_size=5`, { headers: admin_headers });
  check(studentsRes, {
    'students/ returns 200': (r) => r.status === 200,
    'students/ has results array': (r) => Array.isArray(r.json('results')),
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  3. ATTENDANCE (teacher)
  // ══════════════════════════════════════════════════════════════════════════

  const attendanceRes = http.get(`${base}/attendance/?page_size=5`, { headers: teacher_headers });
  check(attendanceRes, {
    'attendance/ returns 200': (r) => r.status === 200,
  });

  const attReportRes = http.get(
    `${base}/attendance/student-report/?student_id=demo&month=1&year=2025`,
    { headers: teacher_headers },
  );
  check(attReportRes, {
    'attendance/student-report returns 200 or 400': (r) => r.status === 200 || r.status === 400,
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  4. FEES (admin)
  // ══════════════════════════════════════════════════════════════════════════

  const feesRes = http.get(`${base}/fees/invoices/?page_size=5`, { headers: admin_headers });
  check(feesRes, {
    'fees/invoices returns 200': (r) => r.status === 200,
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  5. GRADEBOOK (teacher + admin)
  // ══════════════════════════════════════════════════════════════════════════

  const examsRes = http.get(`${base}/gradebook/exams/?page_size=5`, { headers: admin_headers });
  check(examsRes, {
    'gradebook/exams returns 200': (r) => r.status === 200,
  });

  const gradesRes = http.get(`${base}/gradebook/grades/?page_size=5`, { headers: admin_headers });
  check(gradesRes, {
    'gradebook/grades returns 200': (r) => r.status === 200,
  });

  const reportCardsRes = http.get(`${base}/gradebook/report-cards/?page_size=5`, { headers: admin_headers });
  check(reportCardsRes, {
    'gradebook/report-cards returns 200': (r) => r.status === 200,
  });

  const assessmentsRes = http.get(`${base}/gradebook/assessments/?page_size=5`, { headers: teacher_headers });
  check(assessmentsRes, {
    'gradebook/assessments returns 200': (r) => r.status === 200,
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  6. ACADEMICS (teacher)
  // ══════════════════════════════════════════════════════════════════════════

  const subjectsRes = http.get(`${base}/academics/subjects/?page_size=5`, { headers: teacher_headers });
  check(subjectsRes, {
    'academics/subjects returns 200': (r) => r.status === 200,
  });

  const teacherProfilesRes = http.get(`${base}/academics/teacher-profiles/`, { headers: admin_headers });
  check(teacherProfilesRes, {
    'academics/teacher-profiles returns 200': (r) => r.status === 200,
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  7. TIMETABLE (teacher)
  // ══════════════════════════════════════════════════════════════════════════

  const timetableRes = http.get(`${base}/timetable/slots/?page_size=5`, { headers: teacher_headers });
  check(timetableRes, {
    'timetable/slots returns 200': (r) => r.status === 200,
  });

  const eventsRes = http.get(`${base}/timetable/events/?page_size=5`, { headers: teacher_headers });
  check(eventsRes, {
    'timetable/events returns 200': (r) => r.status === 200,
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  8. COMMUNICATION (student)
  // ══════════════════════════════════════════════════════════════════════════

  const announcementsRes = http.get(`${base}/communication/announcements/?page_size=5`, {
    headers: student_headers,
  });
  check(announcementsRes, {
    'communication/announcements returns 200': (r) => r.status === 200,
  });

  const notificationsRes = http.get(`${base}/communication/notifications/?page_size=5`, {
    headers: student_headers,
  });
  check(notificationsRes, {
    'communication/notifications returns 200': (r) => r.status === 200,
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  9. WRITE OPERATION — mark all notifications read (student)
  //     Validates that the full POST cycle works: auth → serialize → write → respond.
  //     Returns 200 even with zero notifications, so no demo data dependency.
  // ══════════════════════════════════════════════════════════════════════════

  const markAllReadRes = http.post(
    `${base}/communication/notifications/mark-all-read/`,
    JSON.stringify({}),
    { headers: student_headers },
  );
  check(markAllReadRes, {
    'communication/notifications/mark-all-read returns 200 (write path OK)': (r) => r.status === 200,
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  10. REPORTING (admin)
  // ══════════════════════════════════════════════════════════════════════════

  const statsRes = http.get(`${base}/reporting/dashboard-stats/`, { headers: admin_headers });
  check(statsRes, {
    'reporting/dashboard-stats returns 200': (r) => r.status === 200,
    'reporting/dashboard-stats has expected keys': (r) => {
      const keys = Object.keys(r.json());
      return ['total_students', 'total_teachers', 'total_classrooms'].every(k => keys.includes(k));
    },
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  11. CSRF-EXEMPT ENDPOINTS UNAUTHENTICATED
  // ══════════════════════════════════════════════════════════════════════════

  const healthRes = http.get(`${base.replace('/api/v1', '')}/health/ready/`);
  check(healthRes, {
    'health/ready returns 200': (r) => r.status === 200,
  });

  // ══════════════════════════════════════════════════════════════════════════
  //  SUMMARY (printed to stdout for CI log parsing)
  // ══════════════════════════════════════════════════════════════════════════

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  Smoke test complete');
  console.log(`  Endpoints checked: 20+`);
  console.log(`  Backend: ${BASE_URL}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  sleep(1);
}
