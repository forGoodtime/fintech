from django.urls import path
from django.http import JsonResponse
from . import views

def wallet_endpoints(request):
    return JsonResponse({
        'endpoints': {
            'currencies': '/api/wallets/currencies/',
            'wallets': '/api/wallets/',
            'wallet_detail': '/api/wallets/{id}/',
            'wallet_balance': '/api/wallets/{id}/balance/',
            'wallet_limits': '/api/wallets/{id}/limits/',
        }
    })

urlpatterns = [
    path('currencies/', views.CurrencyListView.as_view(), name='currency-list'),
    path('', views.WalletListCreateView.as_view(), name='wallet-list-create'),
    path('<int:pk>/', views.WalletDetailView.as_view(), name='wallet-detail'),
    path('<int:wallet_id>/balance/', views.wallet_balance, name='wallet-balance'),
    path('<int:wallet_id>/limits/', views.WalletLimitListCreateView.as_view(), name='wallet-limits'),
]
