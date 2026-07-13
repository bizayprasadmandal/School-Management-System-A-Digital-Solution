import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000/api/v1';

const loginFailureRate = new Rate('login_failures');
const loginDuration = new Trend('login_duration');

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 users
    { duration: '1m', target: 50 },    // Hold at 50 users
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    login_duration: ['p(95)<2000'],  // 95% of logins under 2s
    login_failures: ['rate<0.05'],   // Less than 5% failure rate
    http_req_duration: ['p(95)<3000'],
  },
};

const USERS = [
  { email: 'admin@demo.edusphere.school', password: 'Admin@1234' },
  { email: 'teacher@demo.edusphere.school', password: 'Teacher@1234' },
  { email: 'student@demo.edusphere.school', password: 'Student@1234' },
];

export default function () {
  const user = USERS[Math.floor(Math.random() * USERS.length)];

  // Login
  const loginStart = Date.now();
  const loginRes = http.post(`${BASE_URL}/auth/login/`, {
    email: user.email,
    password: user.password,
  }, {
    tags: { endpoint: 'auth-login' },
  });
  loginDuration.add(Date.now() - loginStart);
  loginFailureRate.add(loginRes.status !== 200);

  check(loginRes, {
    'login status is 200': (r) => r.status === 200,
    'has access token': (r) => r.json('access') !== undefined,
    'has user profile': (r) => r.json('user') !== undefined,
  });

  if (loginRes.status === 200) {
    const token = loginRes.json('access');

    // Get profile
    const profileRes = http.get(`${BASE_URL}/auth/me/`, {
      headers: { Authorization: `Bearer ${token}` },
      tags: { endpoint: 'auth-me' },
    });
    check(profileRes, {
      'profile status is 200': (r) => r.status === 200,
      'has email': (r) => r.json('email') !== undefined,
    });

    // List students
    const studentsRes = http.get(`${BASE_URL}/students/?page_size=10`, {
      headers: { Authorization: `Bearer ${token}` },
      tags: { endpoint: 'students-list' },
    });
    check(studentsRes, {
      'students status is 200': (r) => r.status === 200,
    });

    // Get dashboard stats
    const statsRes = http.get(`${BASE_URL}/reporting/dashboard-stats/`, {
      headers: { Authorization: `Bearer ${token}` },
      tags: { endpoint: 'dashboard-stats' },
    });
    check(statsRes, {
      'dashboard stats status is 200': (r) => r.status === 200,
    });

    // Refresh token
    const refreshRes = http.post(`${BASE_URL}/auth/token/refresh/`, {
      refresh: loginRes.json('refresh'),
    });
    check(refreshRes, {
      'refresh status is 200': (r) => r.status === 200,
    });
  }

  sleep(Math.random() * 3 + 1);  // 1-4 second think time
}
