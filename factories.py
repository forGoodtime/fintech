import factory
from django.contrib.auth import get_user_model
from decimal import Decimal
from wallets.models import Currency, Wallet
from transactions.models import Transaction, TransactionCategory

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    username = factory.Sequence(lambda n: f'user{n}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True


class CurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Currency
    
    code = 'USD'
    name = 'US Dollar'
    symbol = '$'
    is_active = True


class WalletFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Wallet
    
    user = factory.SubFactory(UserFactory)
    currency = factory.SubFactory(CurrencyFactory)
    balance = Decimal('0.00')
    is_active = True


class TransactionCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TransactionCategory
    
    name = factory.Faker('word')
    description = factory.Faker('sentence')
    color = '#FF6B6B'


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction
    
    transaction_type = 'transfer'
    sender = factory.SubFactory(UserFactory)
    receiver = factory.SubFactory(UserFactory)
    amount = Decimal('100.00')
    currency_code = 'USD'
    status = 'completed'
    description = factory.Faker('sentence')
