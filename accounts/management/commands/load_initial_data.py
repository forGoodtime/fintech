from django.core.management.base import BaseCommand
from wallets.models import Currency
from transactions.models import TransactionCategory


class Command(BaseCommand):
    help = 'Load initial data for currencies and transaction categories'
    
    def handle(self, *args, **options):
        currencies = [
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
            {'code': 'KZT', 'name': 'Kazakhstani Tenge', 'symbol': '₸'},
            {'code': 'RUB', 'name': 'Russian Ruble', 'symbol': '₽'},
        ]
        
        for currency_data in currencies:
            currency, created = Currency.objects.get_or_create(
                code=currency_data['code'],
                defaults=currency_data
            )
            if created:
                self.stdout.write(f'Created currency: {currency.code}')
        
        categories = [
            {'name': 'Food & Dining', 'description': 'Restaurants, groceries, food delivery', 'color': '#FF6B6B'},
            {'name': 'Transportation', 'description': 'Gas, public transport, taxi', 'color': '#4ECDC4'},
            {'name': 'Shopping', 'description': 'Clothing, electronics, general shopping', 'color': '#45B7D1'},
            {'name': 'Entertainment', 'description': 'Movies, games, events', 'color': '#96CEB4'},
            {'name': 'Bills & Utilities', 'description': 'Rent, electricity, internet', 'color': '#FFEAA7'},
            {'name': 'Healthcare', 'description': 'Medical expenses, pharmacy', 'color': '#DDA0DD'},
            {'name': 'Education', 'description': 'Books, courses, tuition', 'color': '#98D8C8'},
            {'name': 'Transfer', 'description': 'Money transfers between accounts', 'color': '#F7DC6F'},
            {'name': 'Other', 'description': 'Miscellaneous expenses', 'color': '#AED6F1'},
        ]
        
        for category_data in categories:
            category, created = TransactionCategory.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))
