import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 10 },   // Stay at 10 users
    { duration: '30s', target: 20 },  // Ramp up to 20 users
    { duration: '1m', target: 20 },   // Stay at 20 users
    { duration: '30s', target: 0 },   // Ramp down to 0 users
  ],
};

const BASE_URL = 'http://127.0.0.1:8000';

// Test data
let users = [];
let tokens = [];

export function setup() {
  // Create test users
  for (let i = 0; i < 20; i++) {
    let registerData = {
      email: `loadtest${i}@example.com`,
      username: `loadtest${i}`,
      password: 'testpass123',
      password_confirm: 'testpass123'
    };
    
    let response = http.post(`${BASE_URL}/api/auth/register/`, JSON.stringify(registerData), {
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.status === 201) {
      let data = JSON.parse(response.body);
      users.push(data.user);
      tokens.push(data.token);
    }
  }
  
  return { users, tokens };
}

export default function(data) {
  let userIndex = Math.floor(Math.random() * data.tokens.length);
  let token = data.tokens[userIndex];
  
  let headers = {
    'Content-Type': 'application/json',
    'Authorization': `Token ${token}`
  };
  
  // Test 1: Get wallets
  let walletsResponse = http.get(`${BASE_URL}/api/wallets/`, { headers });
  check(walletsResponse, {
    'wallets status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);
  
  // Test 2: Make deposit
  let depositData = {
    amount: (Math.random() * 1000 + 100).toFixed(2),
    currency_code: 'USD',
    description: 'Load test deposit'
  };
  
  let depositResponse = http.post(`${BASE_URL}/api/transactions/deposit/`, 
    JSON.stringify(depositData), { headers });
  check(depositResponse, {
    'deposit status is 201': (r) => r.status === 201,
  }) || errorRate.add(1);
  
  // Test 3: Get transactions
  let transactionsResponse = http.get(`${BASE_URL}/api/transactions/`, { headers });
  check(transactionsResponse, {
    'transactions status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);
  
  // Test 4: Get analytics
  let analyticsResponse = http.get(`${BASE_URL}/api/analytics/dashboard/`, { headers });
  check(analyticsResponse, {
    'analytics status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);
  
  sleep(1);
}

export function teardown(data) {
  // Cleanup is handled by Django's test database
  console.log('Load test completed');
}
