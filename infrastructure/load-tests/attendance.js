import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000/api/v1';

export const options = {
  stages: [
    { duration: '30s', target: 30 },
    { duration: '1m', target: 80 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000'],
    http_req_failed: ['rate<0.05'],
  },
};

/**
 * setup() runs once before the test starts.
 * We authenticate here and pass the token + headers
 * to the default() function via the returned object.
 */
export function setup() {
  const loginRes = http.post(`${BASE_URL}/auth/login/`, {
    email: 'admin@demo.edusphere.school',
    password: 'Admin@1234',
  });

  if (loginRes.status !== 200) {
    console.error('Setup login failed:', loginRes.status, loginRes.body);
    return { authenticated: false };
  }

  const token = loginRes.json('access');
  return {
    authenticated: true,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };
}

/**
 * default() runs for each VU iteration.
 * The `data` parameter is whatever setup() returned.
 */
export default function (data) {
  if (!data.authenticated) {
    console.warn('Skipping iteration — setup login failed');
    sleep(1);
    return;
  }

  const { headers } = data;

  // List attendance records
  const listRes = http.get(`${BASE_URL}/attendance/?page_size=20`, { headers });
  check(listRes, {
    'attendance list status is 200': (r) => r.status === 200,
  });

  // Get student attendance report
  const reportRes = http.get(
    `${BASE_URL}/attendance/student-report/?student_id=demo&month=1&year=2025`,
    { headers },
  );
  check(reportRes, {
    'student report status is 200 or 400': (r) => r.status === 200 || r.status === 400,
  });

  // Fee endpoints
  const feesRes = http.get(`${BASE_URL}/fees/invoices/?page_size=10`, { headers });
  check(feesRes, {
    'fees list status is 200': (r) => r.status === 200,
  });

  sleep(Math.random() * 2 + 1);
}
