from django.contrib import admin
from .models import UserFinancialSummary, DailyTransactionSummary, MonthlyReport


@admin.register(UserFinancialSummary)
class UserFinancialSummaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_balance', 'transaction_count', 'last_updated']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['last_updated']


@admin.register(DailyTransactionSummary)
class DailyTransactionSummaryAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_transactions', 'total_volume', 'total_fees', 'unique_users']
    list_filter = ['date']
    date_hierarchy = 'date'


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'month', 'transaction_count', 'most_used_category']
    list_filter = ['year', 'month']
    search_fields = ['user__email']
