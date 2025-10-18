import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor
import json

BASE_URL = 'http://127.0.0.1:8000'

class SimpleLoadTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.response_times = []
        self.errors = []
        self.success_count = 0
        self.error_count = 0
        self.lock = threading.Lock()
    
    def register_user(self, user_id):
        """Регистрация пользователя"""
        data = {
            'email': f'loadtest{user_id}@example.com',
            'username': f'loadtest{user_id}',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/register/',
                json=data,
                timeout=10
            )
            response_time = time.time() - start_time
            
            with self.lock:
                self.response_times.append(response_time)
            
            if response.status_code == 201:
                result = response.json()
                return result['token']
            else:
                with self.lock:
                    self.errors.append(f'Registration failed: {response.status_code}')
                return None
        except Exception as e:
            with self.lock:
                self.errors.append(f'Registration error: {str(e)}')
            return None
    
    def test_api_endpoint(self, endpoint, token, method='GET', data=None):
        """Тестирование API endpoint"""
        headers = {'Authorization': f'Token {token}'}
        
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(
                    f'{self.base_url}{endpoint}',
                    headers=headers,
                    timeout=10
                )
            elif method == 'POST':
                response = requests.post(
                    f'{self.base_url}{endpoint}',
                    json=data,
                    headers=headers,
                    timeout=10
                )
            
            response_time = time.time() - start_time
            
            with self.lock:
                self.response_times.append(response_time)
                if response.status_code in [200, 201]:
                    self.success_count += 1
                    return True
                else:
                    self.error_count += 1
                    return False
        except Exception as e:
            with self.lock:
                self.errors.append(f'API error: {str(e)}')
                self.error_count += 1
            return False
    
    def run_user_scenario(self, user_id):
        """Сценарий одного пользователя"""
        # 1. Регистрация
        token = self.register_user(user_id)
        if not token:
            return
        
        # 2. Получение кошельков
        self.test_api_endpoint('/api/wallets/', token)
        
        # 3. Депозит
        deposit_data = {
            'amount': '500.00',
            'currency_code': 'USD',
            'description': f'Load test deposit {user_id}'
        }
        self.test_api_endpoint('/api/transactions/deposit/', token, 'POST', deposit_data)
        
        # 4. Получение транзакций
        self.test_api_endpoint('/api/transactions/', token)
        
        # 5. Аналитика
        self.test_api_endpoint('/api/analytics/dashboard/', token)
    
    def run_load_test(self, concurrent_users=5, total_users=25):
        """Запуск нагрузочного теста"""
        print(f"Starting load test with {concurrent_users} concurrent users, total {total_users} users")
        print(f"Target URL: {self.base_url}")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            for user_id in range(total_users):
                future = executor.submit(self.run_user_scenario, user_id)
                futures.append(future)
            
            # Ждем завершения всех тестов
            for future in futures:
                future.result()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.print_results(total_time)
    
    def print_results(self, total_time):
        """Вывод результатов тестирования"""
        print(f"\n=== LOAD TEST RESULTS ===")
        print(f"Total test time: {total_time:.2f} seconds")
        print(f"Total requests: {len(self.response_times)}")
        print(f"Successful requests: {self.success_count}")
        print(f"Failed requests: {self.error_count}")
        
        if self.response_times:
            avg_time = statistics.mean(self.response_times)
            median_time = statistics.median(self.response_times)
            max_time = max(self.response_times)
            min_time = min(self.response_times)
            
            print(f"Average response time: {avg_time:.3f}s")
            print(f"Median response time: {median_time:.3f}s")
            print(f"Min response time: {min_time:.3f}s")
            print(f"Max response time: {max_time:.3f}s")
            print(f"Requests per second: {len(self.response_times) / total_time:.2f}")
            
            # Percentiles
            sorted_times = sorted(self.response_times)
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
            
            print(f"95th percentile: {p95:.3f}s")
            print(f"99th percentile: {p99:.3f}s")
        
        if self.errors:
            print(f"\nFirst 10 errors:")
            for error in self.errors[:10]:
                print(f"  - {error}")
        
        # Результат
        success_rate = (self.success_count / (self.success_count + self.error_count)) * 100 if (self.success_count + self.error_count) > 0 else 0
        print(f"\nSuccess rate: {success_rate:.1f}%")
        
        if avg_time < 1.0 and success_rate > 95:
            print("✅ Performance test PASSED")
        else:
            print("❌ Performance test FAILED")

def main():
    tester = SimpleLoadTester()
    
    # Проверяем доступность сервера
    try:
        response = requests.get(f'{BASE_URL}/api/auth/register/', timeout=5)
        print(f"Server status check: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("Please make sure Django server is running on http://127.0.0.1:8000")
        return
    
    tester.run_load_test(concurrent_users=3, total_users=15)

if __name__ == "__main__":
    main()
