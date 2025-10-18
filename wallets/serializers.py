from rest_framework import serializers
from .models import Wallet, Currency, WalletLimit


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol', 'is_active']


class WalletSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Wallet
        fields = ['id', 'currency', 'currency_id', 'balance', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']


class WalletLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletLimit
        fields = ['id', 'limit_type', 'amount', 'used_amount', 'reset_date']
        read_only_fields = ['id', 'used_amount']


class WalletDetailSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    limits = WalletLimitSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['id', 'currency', 'balance', 'is_active', 'created_at', 'updated_at', 'limits']
