import asyncio
import aiohttp
import time
import json
from concurrent.futures import ThreadPoolExecutor
import statistics

BASE_URL = 'http://127.0.0.1:8000'

class LoadTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.response_times = []
        self.errors = []
        
    async def register_user(self, session, user_id):
        """Регистрация пользователя"""
        data = {
            'email': f'loadtest{user_id}@example.com',
            'username': f'loadtest{user_id}',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        start_time = time.time()
        try:
            async with session.post(f'{self.base_url}/api/auth/register/', 
                                  json=data) as response:
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                
                if response.status == 201:
                    result = await response.json()
                    return result['token']
                else:
                    self.errors.append(f'Registration failed: {response.status}')
                    return None
        except Exception as e:
            self.errors.append(f'Registration error: {str(e)}')
            return None
    
    async def test_api_endpoint(self, session, endpoint, token, method='GET', data=None):
        """Тестирование API endpoint"""
        headers = {'Authorization': f'Token {token}'}
        
        start_time = time.time()
        try:
            if method == 'GET':
                async with session.get(f'{self.base_url}{endpoint}', 
                                     headers=headers) as response:
                    response_time = time.time() - start_time
                    self.response_times.append(response_time)
                    return response.status == 200
            elif method == 'POST':
                async with session.post(f'{self.base_url}{endpoint}', 
                                      json=data, headers=headers) as response:
                    response_time = time.time() - start_time
                    self.response_times.append(response_time)
                    return response.status in [200, 201]
        except Exception as e:
            self.errors.append(f'API error: {str(e)}')
            return False
    
    async def run_user_scenario(self, session, user_id):
        """Сценарий одного пользователя"""
        # 1. Регистрация
        token = await self.register_user(session, user_id)
        if not token:
            return
        
        # 2. Получение кошельков
        await self.test_api_endpoint(session, '/api/wallets/', token)
        
        # 3. Депозит
        deposit_data = {
            'amount': '500.00',
            'currency_code': 'USD',
            'description': f'Load test deposit {user_id}'
        }
        await self.test_api_endpoint(session, '/api/transactions/deposit/', 
                                   token, 'POST', deposit_data)
        
        # 4. Получение транзакций
        await self.test_api_endpoint(session, '/api/transactions/', token)
        
        # 5. Аналитика
        await self.test_api_endpoint(session, '/api/analytics/dashboard/', token)
    
    async def run_load_test(self, concurrent_users=10, duration=60):
        """Запуск нагрузочного теста"""
        print(f"Starting load test with {concurrent_users} concurrent users for {duration} seconds")
        
        start_time = time.time()
        connector = aiohttp.TCPConnector(limit=100)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            user_id = 0
            
            while time.time() - start_time < duration:
                # Создаем задачи для пользователей
                for _ in range(concurrent_users):
                    task = asyncio.create_task(
                        self.run_user_scenario(session, user_id)
                    )
                    tasks.append(task)
                    user_id += 1
                
                # Ждем немного между волнами
                await asyncio.sleep(5)
            
            # Ждем завершения всех задач
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.print_results()
    
    def print_results(self):
        """Вывод результатов тестирования"""
        if self.response_times:
            avg_time = statistics.mean(self.response_times)
            median_time = statistics.median(self.response_times)
            max_time = max(self.response_times)
            min_time = min(self.response_times)
            
            print(f"\n=== LOAD TEST RESULTS ===")
            print(f"Total requests: {len(self.response_times)}")
            print(f"Average response time: {avg_time:.3f}s")
            print(f"Median response time: {median_time:.3f}s")
            print(f"Min response time: {min_time:.3f}s")
            print(f"Max response time: {max_time:.3f}s")
            print(f"Total errors: {len(self.errors)}")
            
            if self.errors:
                print(f"\nErrors:")
                for error in self.errors[:10]:  # Show first 10 errors
                    print(f"  - {error}")
        else:
            print("No requests completed successfully")

async def main():
    tester = LoadTester()
    await tester.run_load_test(concurrent_users=5, duration=30)

if __name__ == "__main__":
    asyncio.run(main())
