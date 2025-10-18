from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from decimal import Decimal
from .models import Transaction, TransactionCategory
from wallets.models import Currency, Wallet

User = get_user_model()


class TransactionTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='testpass123'
        )
        
        self.token1 = Token.objects.create(user=self.user1)
        
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$'
        )
        
        self.wallet1 = Wallet.objects.create(
            user=self.user1,
            currency=self.currency,
            balance=Decimal('1000.00')
        )
        self.wallet2 = Wallet.objects.create(
            user=self.user2,
            currency=self.currency,
            balance=Decimal('100.00')
        )
        
        self.category = TransactionCategory.objects.create(
            name='Transfer',
            description='Money transfer'
        )
    
    def test_create_deposit(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = '/api/transactions/deposit/'
        data = {
            'amount': '500.00',
            'currency_code': 'USD',
            'description': 'Test deposit'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_transactions(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        Transaction.objects.create(
            transaction_type='deposit',
            receiver=self.user1,
            amount=Decimal('100.00'),
            currency_code='USD'
        )
        
        url = '/api/transactions/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
