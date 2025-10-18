from django.urls import path
from django.http import JsonResponse
from . import views

def analytics_endpoints(request):
    return JsonResponse({
        'endpoints': {
            'summary': '/api/analytics/summary/',
            'dashboard': '/api/analytics/dashboard/',
            'transaction_analytics': '/api/analytics/transaction-analytics/',
            'monthly_reports': '/api/analytics/monthly-reports/',
            'daily_summary': '/api/analytics/daily-summary/',
        }
    })

urlpatterns = [
    path('', analytics_endpoints, name='analytics-endpoints'),
    path('summary/', views.UserFinancialSummaryView.as_view(), name='financial-summary'),
    path('dashboard/', views.dashboard_stats, name='dashboard-stats'),
    path('transaction-analytics/', views.transaction_analytics, name='transaction-analytics'),
    path('monthly-reports/', views.MonthlyReportListView.as_view(), name='monthly-reports'),
    path('daily-summary/', views.DailyTransactionSummaryView.as_view(), name='daily-summary'),
]
