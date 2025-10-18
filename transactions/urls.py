from django.urls import path
from django.http import JsonResponse
from . import views

def transaction_endpoints(request):
    return JsonResponse({
        'endpoints': {
            'categories': '/api/transactions/categories/',
            'transactions': '/api/transactions/',
            'transaction_detail': '/api/transactions/{uuid}/',
            'transfer': '/api/transactions/transfer/',
            'deposit': '/api/transactions/deposit/',
            'withdrawal': '/api/transactions/withdrawal/',
        }
    })

urlpatterns = [
    path('categories/', views.TransactionCategoryListView.as_view(), name='transaction-categories'),
    path('', views.TransactionListView.as_view(), name='transaction-list'),
    path('<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('transfer/', views.create_transfer, name='create-transfer'),
    path('deposit/', views.create_deposit, name='create-deposit'),
    path('withdrawal/', views.create_withdrawal, name='create-withdrawal'),
]
