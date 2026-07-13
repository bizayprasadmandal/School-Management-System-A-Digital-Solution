import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000/api/v1';

// ── Custom metrics ──────────────────────────────────────────────────────────

const timetableRequestDuration = new Trend('timetable_req_duration');
const timetableErrors = new Rate('timetable_errors');

// ── Options ──────────────────────────────────────────────────────────────────

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 VUs (lighter than auth)
    { duration: '1m',  target: 60 },   // Hold at 60 VUs (read-heavy, light queries)
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    timetable_req_duration: ['p(95)<4000'],
    timetable_errors:       ['rate<0.05'],
    http_req_duration:      ['p(95)<5000'],
    http_req_failed:        ['rate<0.05'],
  },
};

// ── Setup: Authenticate admin + teacher, fetch reference IDs ─────────────────

export function setup() {
  // Admin login — for full CRUD endpoints
  const adminLogin = http.post(`${BASE_URL}/auth/login/`, {
    email: 'admin@demo.edusphere.school',
    password: 'Admin@1234',
  });

  if (adminLogin.status !== 200) {
    console.error('Admin login failed:', adminLogin.status);
    return { authenticated: false };
  }
  const adminToken = adminLogin.json('access');
  const adminHeaders = {
    Authorization: `Bearer ${adminToken}`,
    'Content-Type': 'application/json',
  };

  // Teacher login — for teacher-scoped schedule endpoint
  const teacherLogin = http.post(`${BASE_URL}/auth/login/`, {
    email: 'teacher@demo.edusphere.school',
    password: 'Teacher@1234',
  });

  let teacherHeaders = null;
  let teacherId = null;
  if (teacherLogin.status === 200) {
    const teacherToken = teacherLogin.json('access');
    teacherHeaders = {
      Authorization: `Bearer ${teacherToken}`,
      'Content-Type': 'application/json',
    };
    // Extract teacher ID from the profile for teacher-schedule endpoint
    const profileRes = http.get(`${BASE_URL}/auth/me/`, { headers: teacherHeaders });
    if (profileRes.status === 200) {
      teacherId = profileRes.json('id');
    }
  }

  // Fetch first classroom and academic year IDs for detail endpoints
  const studentsRes = http.get(`${BASE_URL}/students/?page_size=5`, {
    headers: adminHeaders,
    tags: { endpoint: 'setup-classrooms' },
  });

  let firstClassroomId = null;
  let firstAcademicYearId = null;
  if (studentsRes.status === 200) {
    const results = studentsRes.json('results') || [];
    if (results.length > 0) {
      const student = results[0];
      // Students have a `current_classroom` → use its ID
      // If that's not available, fall back to classroom from any enrollment
      if (student.current_classroom) {
        firstClassroomId = typeof student.current_classroom === 'object'
          ? student.current_classroom.id
          : student.current_classroom;
      }
      // Academic year from enrollments or student record
      if (student.current_academic_year) {
        firstAcademicYearId = typeof student.current_academic_year === 'object'
          ? student.current_academic_year.id
          : student.current_academic_year;
      }
    }
  }

  // Fallback: try to get a classroom ID from the timetable slots endpoint
  if (!firstClassroomId) {
    const slotsRes = http.get(`${BASE_URL}/timetable/slots/?page_size=1`, {
      headers: adminHeaders,
      tags: { endpoint: 'setup-slots' },
    });
    if (slotsRes.status === 200) {
      const slots = slotsRes.json('results') || [];
      if (slots.length > 0) {
        firstClassroomId = slots[0].classroom;
        if (!firstAcademicYearId) {
          firstAcademicYearId = slots[0].academic_year;
        }
      }
    }
  }

  return {
    authenticated: adminLogin.status === 200,
    adminHeaders,
    teacherHeaders,
    teacherId,
    firstClassroomId,
    firstAcademicYearId,
  };
}

// ── Simulated timetable browsing user ────────────────────────────────────────

export default function (data) {
  if (!data.authenticated) {
    console.warn('Skipping iteration — setup login failed');
    sleep(1);
    return;
  }

  const { adminHeaders, teacherHeaders, teacherId, firstClassroomId, firstAcademicYearId } = data;
  const headers = Math.random() < 0.3 && teacherHeaders ? teacherHeaders : adminHeaders;
  const base = BASE_URL;

  // ── 1. List periods (lightweight, always returns) ─────────────────────────
  const t1 = Date.now();
  const periodsRes = http.get(`${base}/timetable/periods/`, {
    headers,
    tags: { endpoint: 'timetable-periods-list' },
  });
  timetableRequestDuration.add(Date.now() - t1);
  timetableErrors.add(periodsRes.status >= 400);

  check(periodsRes, {
    'list periods status is 200': (r) => r.status === 200,
    'periods has data': (r) => {
      const body = r.json();
      return Array.isArray(body) || Array.isArray(body?.results);
    },
  });

  // ── 2. List timetable slots (paginated, filterable) ──────────────────────
  const t2 = Date.now();
  const slotsRes = http.get(`${base}/timetable/slots/?page_size=20`, {
    headers,
    tags: { endpoint: 'timetable-slots-list' },
  });
  timetableRequestDuration.add(Date.now() - t2);
  timetableErrors.add(slotsRes.status >= 400);

  check(slotsRes, {
    'list slots status is 200': (r) => r.status === 200,
    'slots have results array': (r) => Array.isArray(r.json('results')),
  });

  // ── 3. Filter slots by a specific day (simulates browsing by day) ────────
  const dayOfWeek = Math.floor(Math.random() * 6); // 0=Mon..5=Sat
  const t3 = Date.now();
  const slotsFilteredRes = http.get(
    `${base}/timetable/slots/?day_of_week=${dayOfWeek}&page_size=20`,
    { headers, tags: { endpoint: 'timetable-slots-filtered' } },
  );
  timetableRequestDuration.add(Date.now() - t3);
  timetableErrors.add(slotsFilteredRes.status >= 400);

  check(slotsFilteredRes, {
    'filter slots by day status is 200': (r) => r.status === 200,
  });

  // ── 4. Weekly timetable for a classroom (if ID available) ─────────────────
  if (firstClassroomId) {
    const params = firstAcademicYearId
      ? `?classroom_id=${firstClassroomId}&academic_year_id=${firstAcademicYearId}`
      : `?classroom_id=${firstClassroomId}`;

    const t4 = Date.now();
    const weeklyRes = http.get(`${base}/timetable/slots/weekly/${params}`, {
      headers,
      tags: { endpoint: 'timetable-weekly' },
    });
    timetableRequestDuration.add(Date.now() - t4);
    timetableErrors.add(weeklyRes.status >= 400);

    check(weeklyRes, {
      'weekly timetable status is 200': (r) => r.status === 200,
      'weekly has Monday key': (r) => r.status === 200 && r.json('Monday') !== undefined,
    });
  }

  // ── 5. Teacher schedule ──────────────────────────────────────────────────
  if (teacherId) {
    const t5 = Date.now();
    const teacherScheduleRes = http.get(
      `${base}/timetable/slots/teacher-schedule/?teacher_id=${teacherId}`,
      { headers, tags: { endpoint: 'timetable-teacher-schedule' } },
    );
    timetableRequestDuration.add(Date.now() - t5);
    timetableErrors.add(teacherScheduleRes.status >= 400);

    check(teacherScheduleRes, {
      'teacher schedule status is 200': (r) => r.status === 200,
      'teacher schedule is array': (r) => r.status === 200 && Array.isArray(r.json()),
    });
  }

  // ── 6. List school events (paginated, with default ordering) ─────────────
  const t6 = Date.now();
  const eventsRes = http.get(`${base}/timetable/events/?page_size=10`, {
    headers,
    tags: { endpoint: 'timetable-events-list' },
  });
  timetableRequestDuration.add(Date.now() - t6);
  timetableErrors.add(eventsRes.status >= 400);

  check(eventsRes, {
    'list events status is 200': (r) => r.status === 200,
    'events have results array': (r) => Array.isArray(r.json('results')),
  });

  // ── 7. Upcoming events (lightweight, top 10) ─────────────────────────────
  const t7 = Date.now();
  const upcomingRes = http.get(`${base}/timetable/events/upcoming/`, {
    headers,
    tags: { endpoint: 'timetable-events-upcoming' },
  });
  timetableRequestDuration.add(Date.now() - t7);
  timetableErrors.add(upcomingRes.status >= 400);

  check(upcomingRes, {
    'upcoming events status is 200': (r) => r.status === 200,
    'upcoming events is array': (r) => Array.isArray(r.json()),
  });

  // ── 8. Write operation — create an event (admin only, 10% chance) ───────
  // Uses adminHeaders to ensure write succeeds; exercises POST path.
  if (Math.random() < 0.1) {
    const now = new Date();
    const startDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    const endDate = startDate; // single-day event

    const t8 = Date.now();
    const createRes = http.post(
      `${base}/timetable/events/`,
      JSON.stringify({
        title: `Load Test Event — ${__VU}-${__ITER}`,
        description: 'Automated event created during k6 load test',
        event_type: 'other',
        start_date: startDate,
        end_date: endDate,
        is_school_wide: true,
      }),
      {
        headers: adminHeaders,
        tags: { endpoint: 'timetable-events-create' },
      },
    );
    timetableRequestDuration.add(Date.now() - t8);
    // Only count 5xx as errors for write operations
    timetableErrors.add(createRes.status >= 500);

    check(createRes, {
      'create event status is 201 or 400': (r) => r.status === 201 || r.status === 400,
    });
  }

  // Simulate user reading the timetable between actions
  sleep(Math.random() * 2 + 1);
}
