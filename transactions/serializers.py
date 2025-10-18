from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Transaction, TransactionCategory, TransactionLog

User = get_user_model()


class TransactionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionCategory
        fields = ['id', 'name', 'description', 'color']


class TransactionLogSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = TransactionLog
        fields = ['id', 'status_from', 'status_to', 'reason', 'created_by_email', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    receiver_email = serializers.CharField(source='receiver.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    logs = TransactionLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'sender_email', 'receiver_email', 'amount', 
                 'fee', 'currency_code', 'category_name', 'description', 'reference_id', 
                 'status', 'metadata', 'created_at', 'updated_at', 'processed_at', 'logs']
        read_only_fields = ['id', 'fee', 'status', 'created_at', 'updated_at', 'processed_at']


class TransferCreateSerializer(serializers.Serializer):
    receiver_email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)
    currency_code = serializers.CharField(max_length=3)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_receiver_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Receiver not found")
        return value
    
    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user.email == attrs['receiver_email']:
            raise serializers.ValidationError("Cannot transfer to yourself")
        return attrs


class DepositCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)
    currency_code = serializers.CharField(max_length=3)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    payment_method = serializers.CharField(max_length=50, required=False)


class WithdrawalCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)
    currency_code = serializers.CharField(max_length=3)
    destination = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
