from django.contrib import admin
from .models import TransactionCategory, Transaction, TransactionLog


@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'color']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction_type', 'sender', 'receiver', 'amount', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'currency_code', 'created_at']
    search_fields = ['sender__email', 'receiver__email', 'reference_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'processed_at']
    date_hierarchy = 'created_at'


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'status_from', 'status_to', 'created_by', 'created_at']
    list_filter = ['status_from', 'status_to', 'created_at']
    search_fields = ['transaction__id', 'created_by__email']
    readonly_fields = ['created_at']
