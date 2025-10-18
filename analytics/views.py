from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import UserFinancialSummary, DailyTransactionSummary, MonthlyReport
from .serializers import (
    UserFinancialSummarySerializer, DailyTransactionSummarySerializer,
    MonthlyReportSerializer, DashboardStatsSerializer, TransactionAnalyticsSerializer
)
from transactions.models import Transaction
from wallets.models import Wallet


class UserFinancialSummaryView(generics.RetrieveAPIView):
    serializer_class = UserFinancialSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        summary, created = UserFinancialSummary.objects.get_or_create(user=self.request.user)
        return summary


@api_view(['GET'])
def dashboard_stats(request):
    user = request.user
    
    total_balance = Wallet.objects.filter(user=user).aggregate(
        total=Sum('balance')
    )['total'] or 0
    
    pending_transactions = Transaction.objects.filter(
        sender=user, status='pending'
    ).count()
    
    current_month = timezone.now().replace(day=1)
    monthly_sent = Transaction.objects.filter(
        sender=user,
        status='completed',
        created_at__gte=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_received = Transaction.objects.filter(
        receiver=user,
        status='completed',
        created_at__gte=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    recent_transactions = Transaction.objects.filter(
        sender=user
    ).order_by('-created_at')[:5]
    
    recent_data = [{
        'id': str(t.id),
        'type': t.transaction_type,
        'amount': str(t.amount),
        'status': t.status,
        'created_at': t.created_at
    } for t in recent_transactions]
    
    data = {
        'total_balance': total_balance,
        'pending_transactions': pending_transactions,
        'monthly_sent': monthly_sent,
        'monthly_received': monthly_received,
        'recent_transactions': recent_data
    }
    
    serializer = DashboardStatsSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
def transaction_analytics(request):
    user = request.user
    period = request.GET.get('period', 'month')
    
    if period == 'week':
        start_date = timezone.now() - timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now() - timedelta(days=30)
    elif period == 'year':
        start_date = timezone.now() - timedelta(days=365)
    else:
        start_date = timezone.now() - timedelta(days=30)
    
    transactions = Transaction.objects.filter(
        sender=user,
        status='completed',
        created_at__gte=start_date
    )
    
    analytics = transactions.aggregate(
        total_amount=Sum('amount'),
        transaction_count=Count('id'),
        average_amount=Avg('amount')
    )
    
    category_breakdown = {}
    for transaction in transactions:
        category = transaction.category.name if transaction.category else 'Other'
        if category in category_breakdown:
            category_breakdown[category] += float(transaction.amount)
        else:
            category_breakdown[category] = float(transaction.amount)
    
    data = {
        'period': period,
        'total_amount': analytics['total_amount'] or 0,
        'transaction_count': analytics['transaction_count'] or 0,
        'average_amount': analytics['average_amount'] or 0,
        'category_breakdown': category_breakdown
    }
    
    serializer = TransactionAnalyticsSerializer(data)
    return Response(serializer.data)


class MonthlyReportListView(generics.ListAPIView):
    serializer_class = MonthlyReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MonthlyReport.objects.filter(user=self.request.user)


class DailyTransactionSummaryView(generics.ListAPIView):
    queryset = DailyTransactionSummary.objects.all()
    serializer_class = DailyTransactionSummarySerializer
    permission_classes = [permissions.IsAdminUser]
