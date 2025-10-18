from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class UserFinancialSummary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='financial_summary')
    total_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_sent = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_received = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_fees_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    transaction_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} Summary"


class DailyTransactionSummary(models.Model):
    date = models.DateField()
    total_transactions = models.PositiveIntegerField(default=0)
    total_volume = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_fees = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    unique_users = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date}: {self.total_transactions} transactions"


class MonthlyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_reports')
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    total_sent = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_received = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    transaction_count = models.PositiveIntegerField(default=0)
    most_used_category = models.CharField(max_length=50, blank=True)
    
    class Meta:
        unique_together = ['user', 'year', 'month']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.user.email} - {self.year}/{self.month}"
