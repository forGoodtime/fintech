from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from decimal import Decimal
from .models import Currency, Wallet, WalletLimit

User = get_user_model()


class WalletTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$'
        )
    
    def test_create_wallet(self):
        url = '/api/wallets/'
        data = {
            'currency_id': self.currency.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Wallet.objects.filter(user=self.user, currency=self.currency).exists())
    
    def test_list_wallets(self):
        Wallet.objects.create(user=self.user, currency=self.currency)
        url = '/api/wallets/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_wallet_balance(self):
        wallet = Wallet.objects.create(
            user=self.user, 
            currency=self.currency, 
            balance=Decimal('100.00')
        )
        url = f'/api/wallets/{wallet.id}/balance/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], Decimal('100.00'))
    
    def test_wallet_detail(self):
        wallet = Wallet.objects.create(user=self.user, currency=self.currency)
        url = f'/api/wallets/{wallet.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['currency']['code'], 'USD')
    
    def test_currencies_list(self):
        url = '/api/wallets/currencies/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['code'], 'USD')
