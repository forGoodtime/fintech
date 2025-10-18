from rest_framework import serializers
from .models import UserFinancialSummary, DailyTransactionSummary, MonthlyReport


class UserFinancialSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFinancialSummary
        fields = ['total_balance', 'total_sent', 'total_received', 'total_fees_paid', 
                 'transaction_count', 'last_updated']


class DailyTransactionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyTransactionSummary
        fields = ['date', 'total_transactions', 'total_volume', 'total_fees', 'unique_users']


class MonthlyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyReport
        fields = ['year', 'month', 'total_sent', 'total_received', 'transaction_count', 
                 'most_used_category']


class DashboardStatsSerializer(serializers.Serializer):
    total_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_transactions = serializers.IntegerField()
    monthly_sent = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_received = serializers.DecimalField(max_digits=15, decimal_places=2)
    recent_transactions = serializers.ListField()


class TransactionAnalyticsSerializer(serializers.Serializer):
    period = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()
    average_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    category_breakdown = serializers.DictField()
