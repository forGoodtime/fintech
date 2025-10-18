from django.contrib import admin
from .models import Currency, Wallet, WalletLimit


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency', 'balance', 'is_active', 'created_at']
    list_filter = ['currency', 'is_active', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WalletLimit)
class WalletLimitAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'limit_type', 'amount', 'used_amount', 'reset_date']
    list_filter = ['limit_type']
    search_fields = ['wallet__user__email']
