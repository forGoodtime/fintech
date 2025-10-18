from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Wallet, Currency, WalletLimit
from .serializers import WalletSerializer, CurrencySerializer, WalletDetailSerializer, WalletLimitSerializer


class CurrencyListView(generics.ListAPIView):
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAuthenticated]


class WalletListCreateView(generics.ListCreateAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['currency', 'is_active']
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WalletDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = WalletDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


@api_view(['GET'])
def wallet_balance(request, wallet_id):
    try:
        wallet = Wallet.objects.get(id=wallet_id, user=request.user)
        return Response({
            'wallet_id': wallet.id,
            'balance': wallet.balance,
            'currency': wallet.currency.code
        })
    except Wallet.DoesNotExist:
        return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)


class WalletLimitListCreateView(generics.ListCreateAPIView):
    serializer_class = WalletLimitSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        wallet_id = self.kwargs.get('wallet_id')
        return WalletLimit.objects.filter(wallet_id=wallet_id, wallet__user=self.request.user)
    
    def perform_create(self, serializer):
        wallet_id = self.kwargs.get('wallet_id')
        wallet = Wallet.objects.get(id=wallet_id, user=self.request.user)
        serializer.save(wallet=wallet)
