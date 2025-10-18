from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.validators import MinValueValidator

User = get_user_model()


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'currency']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.currency.code}: {self.balance}"


class WalletLimit(models.Model):
    LIMIT_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='limits')
    limit_type = models.CharField(max_length=10, choices=LIMIT_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    used_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    reset_date = models.DateTimeField()
    
    def __str__(self):
        return f"{self.wallet} - {self.limit_type}: {self.amount}"
