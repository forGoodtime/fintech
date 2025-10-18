from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Transaction, TransactionCategory
from .serializers import (
    TransactionSerializer, TransactionCategorySerializer, 
    TransferCreateSerializer, DepositCreateSerializer, WithdrawalCreateSerializer
)
from wallets.models import Wallet

User = get_user_model()


class TransactionCategoryListView(generics.ListAPIView):
    queryset = TransactionCategory.objects.all()
    serializer_class = TransactionCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['transaction_type', 'status', 'currency_code']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(
            Q(sender=user) | Q(receiver=user)
        )


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(
            Q(sender=user) | Q(receiver=user)
        )


@api_view(['POST'])
def create_transfer(request):
    serializer = TransferCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        try:
            with transaction.atomic():
                sender = request.user
                receiver = User.objects.get(email=serializer.validated_data['receiver_email'])
                amount = serializer.validated_data['amount']
                currency_code = serializer.validated_data['currency_code']
                
                sender_wallet = Wallet.objects.get(user=sender, currency__code=currency_code)
                receiver_wallet = Wallet.objects.get(user=receiver, currency__code=currency_code)
                
                if sender_wallet.balance < amount:
                    return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
                
                fee = amount * Decimal('0.01')
                
                transfer = Transaction.objects.create(
                    transaction_type='transfer',
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    fee=fee,
                    currency_code=currency_code,
                    description=serializer.validated_data.get('description', ''),
                    status='processing'
                )
                
                sender_wallet.balance -= (amount + fee)
                receiver_wallet.balance += amount
                sender_wallet.save()
                receiver_wallet.save()
                
                transfer.status = 'completed'
                transfer.save()
                
                return Response(TransactionSerializer(transfer).data, status=status.HTTP_201_CREATED)
                
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_deposit(request):
    serializer = DepositCreateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = request.user
            amount = serializer.validated_data['amount']
            currency_code = serializer.validated_data['currency_code']
            
            wallet = Wallet.objects.get(user=user, currency__code=currency_code)
            
            deposit = Transaction.objects.create(
                transaction_type='deposit',
                receiver=user,
                amount=amount,
                currency_code=currency_code,
                description=serializer.validated_data.get('description', ''),
                status='completed'
            )
            
            wallet.balance += amount
            wallet.save()
            
            return Response(TransactionSerializer(deposit).data, status=status.HTTP_201_CREATED)
            
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_withdrawal(request):
    serializer = WithdrawalCreateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = request.user
            amount = serializer.validated_data['amount']
            currency_code = serializer.validated_data['currency_code']
            
            wallet = Wallet.objects.get(user=user, currency__code=currency_code)
            
            if wallet.balance < amount:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            
            withdrawal = Transaction.objects.create(
                transaction_type='withdrawal',
                sender=user,
                amount=amount,
                currency_code=currency_code,
                description=serializer.validated_data.get('description', ''),
                status='processing'
            )
            
            wallet.balance -= amount
            wallet.save()
            
            withdrawal.status = 'completed'
            withdrawal.save()
            
            return Response(TransactionSerializer(withdrawal).data, status=status.HTTP_201_CREATED)
            
        except Wallet.DoesNotExist:
            return Response({'error': 'Wallet not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
