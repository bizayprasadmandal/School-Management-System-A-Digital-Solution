import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000/api/v1';

// ── Custom metrics ──────────────────────────────────────────────────────────

const gradebookRequestDuration = new Trend('gradebook_req_duration');
// Tracks server errors (5xx) on read-only GET endpoints.
// The grade submission POST is excluded because it may return 4xx
// when demo data has no exam schedules (expected, not an error).
const gradebookErrors = new Rate('gradebook_errors');
const gradebookSubmitErrors = new Rate('gradebook_submit_errors');

// ── Options ──────────────────────────────────────────────────────────────────

export const options = {
  stages: [
    { duration: '30s', target: 15 },   // Ramp up to 15 VUs (gradebook is read-heavy)
    { duration: '1m',  target: 40 },   // Hold at 40 VUs
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    gradebook_req_duration: ['p(95)<4000'],
    gradebook_errors:       ['rate<0.05'],
    http_req_duration:      ['p(95)<5000'],
    http_req_failed:        ['rate<0.05'],
  },
};

// ── Setup: Authenticate admin + teacher once, share across VUs ──────────────

export function setup() {
  // Admin login — for read-only listing endpoints
  const adminLogin = http.post(`${BASE_URL}/auth/login/`, {
    email: 'admin@demo.edusphere.school',
    password: 'Admin@1234',
  });

  if (adminLogin.status !== 200) {
    console.error('Admin login failed:', adminLogin.status);
    return { authenticated: false };
  }
  const adminToken = adminLogin.json('access');

  // Teacher login — required for grade submission (POST /gradebook/grades/bulk/)
  const teacherLogin = http.post(`${BASE_URL}/auth/login/`, {
    email: 'teacher@demo.edusphere.school',
    password: 'Teacher@1234',
  });

  if (teacherLogin.status !== 200) {
    console.error('Teacher login failed:', teacherLogin.status);
    return {
      authenticated: true,
      adminHeaders: { Authorization: `Bearer ${adminToken}`, 'Content-Type': 'application/json' },
      teacherHeaders: null,
      firstExamId: null,
    };
  }
  const teacherToken = teacherLogin.json('access');

  // Fetch first exam ID for detail endpoints
  const examsRes = http.get(`${BASE_URL}/gradebook/exams/?page_size=5`, {
    headers: { Authorization: `Bearer ${adminToken}` },
    tags: { endpoint: 'setup-exams' },
  });

  let firstExamId = null;
  if (examsRes.status === 200) {
    const exams = examsRes.json('results') || [];
    if (exams.length > 0) {
      firstExamId = exams[0].id;
    }
  }

  return {
    authenticated: true,
    adminHeaders: {
      Authorization: `Bearer ${adminToken}`,
      'Content-Type': 'application/json',
    },
    teacherHeaders: {
      Authorization: `Bearer ${teacherToken}`,
      'Content-Type': 'application/json',
    },
    firstExamId,
  };
}

// ── Simulated gradebook browsing user ────────────────────────────────────────

export default function (data) {
  if (!data.authenticated) {
    console.warn('Skipping iteration — setup login failed');
    sleep(1);
    return;
  }

  const { adminHeaders, teacherHeaders, firstExamId } = data;
  const base = BASE_URL;

  // ── 1. List exams (admin role) ───────────────────────────────────────────
  const t1 = Date.now();
  const examsRes = http.get(`${base}/gradebook/exams/?page_size=10`, {
    headers: adminHeaders,
    tags: { endpoint: 'gradebook-exams-list' },
  });
  gradebookRequestDuration.add(Date.now() - t1);
  gradebookErrors.add(examsRes.status >= 400);

  check(examsRes, {
    'list exams status is 200': (r) => r.status === 200,
    'exams have results array': (r) => Array.isArray(r.json('results')),
  });

  // ── 2. List grades ──────────────────────────────────────────────────────
  const t2 = Date.now();
  const gradesRes = http.get(`${base}/gradebook/grades/?page_size=10`, {
    headers: adminHeaders,
    tags: { endpoint: 'gradebook-grades-list' },
  });
  gradebookRequestDuration.add(Date.now() - t2);
  gradebookErrors.add(gradesRes.status >= 400);

  check(gradesRes, {
    'list grades status is 200': (r) => r.status === 200,
  });

  // ── 3. List report cards ────────────────────────────────────────────────
  const t3 = Date.now();
  const reportCardsRes = http.get(`${base}/gradebook/report-cards/?page_size=10`, {
    headers: adminHeaders,
    tags: { endpoint: 'gradebook-report-cards' },
  });
  gradebookRequestDuration.add(Date.now() - t3);
  gradebookErrors.add(reportCardsRes.status >= 400);

  check(reportCardsRes, {
    'list report-cards status is 200': (r) => r.status === 200,
  });

  // ── 4. Exam leaderboard (if exam ID available) ──────────────────────────
  if (firstExamId) {
    const t4 = Date.now();
    const leaderboardRes = http.get(
      `${base}/gradebook/exams/${firstExamId}/leaderboard/?limit=10`,
      { headers: adminHeaders, tags: { endpoint: 'gradebook-leaderboard' } },
    );
    gradebookRequestDuration.add(Date.now() - t4);
    gradebookErrors.add(leaderboardRes.status >= 400);

    check(leaderboardRes, {
      'leaderboard status is 200': (r) => r.status === 200,
      'leaderboard is array': (r) => Array.isArray(r.json()),
    });
  }

  // ── 5. List assessments ─────────────────────────────────────────────────
  const t5 = Date.now();
  const assessmentsRes = http.get(`${base}/gradebook/assessments/?page_size=10`, {
    headers: adminHeaders,
    tags: { endpoint: 'gradebook-assessments' },
  });
  gradebookRequestDuration.add(Date.now() - t5);
  gradebookErrors.add(assessmentsRes.status >= 400);

  check(assessmentsRes, {
    'list assessments status is 200': (r) => r.status === 200,
  });

  // ── 6. Grade submission (teacher role) ──────────────────────────────────
  // Attempt to submit a bulk grade. With seeded demo data this may 404 if
  // no exam schedule exists, but it still exercises the POST endpoint and
  // its permission checks under load. We accept 201, 400, or 403 as valid
  // responses (the endpoint is being hit regardless).
  const t6 = Date.now();
  const gradeSubmitRes = http.post(
    `${base}/gradebook/grades/bulk/`,
    JSON.stringify({
      exam_schedule_id: '00000000-0000-0000-0000-000000000000',
      grades: [{ student_id: 'demo', marks_obtained: '85.0', is_absent: false }],
    }),
    {
      headers: teacherHeaders || adminHeaders,
      tags: { endpoint: 'gradebook-grades-submit' },
    },
  );
  gradebookRequestDuration.add(Date.now() - t6);
  gradebookSubmitErrors.add(gradeSubmitRes.status >= 500);  // Track separately from read endpoints

  check(gradeSubmitRes, {
    'grade submit is not a server error': (r) => r.status < 500,
  });

  // Simulate user reading time between actions
  sleep(Math.random() * 2 + 1);
}
