from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum, Count
from decimal import Decimal
from .models import Transaction, TransactionLog
from wallets.models import Wallet
from analytics.models import UserFinancialSummary

User = get_user_model()


@shared_task
def process_transaction(transaction_id):
    try:
        with transaction.atomic():
            trans = Transaction.objects.select_for_update().get(id=transaction_id)
            
            if trans.status != 'pending':
                return f"Transaction {transaction_id} is not pending"
            
            trans.status = 'processing'
            trans.save()
            
            TransactionLog.objects.create(
                transaction=trans,
                status_from='pending',
                status_to='processing',
                reason='Auto processing'
            )
            
            if trans.transaction_type == 'transfer':
                sender_wallet = Wallet.objects.get(user=trans.sender, currency__code=trans.currency_code)
                receiver_wallet = Wallet.objects.get(user=trans.receiver, currency__code=trans.currency_code)
                
                if sender_wallet.balance >= trans.amount:
                    sender_wallet.balance -= trans.amount
                    receiver_wallet.balance += trans.amount
                    
                    sender_wallet.save()
                    receiver_wallet.save()
                    
                    trans.status = 'completed'
                    trans.save()
                    
                    TransactionLog.objects.create(
                        transaction=trans,
                        status_from='processing',
                        status_to='completed',
                        reason='Transfer completed successfully'
                    )
                    
                    update_financial_summaries.delay(trans.sender.id)
                    update_financial_summaries.delay(trans.receiver.id)
                    
                    return f"Transfer {transaction_id} completed successfully"
                else:
                    trans.status = 'failed'
                    trans.save()
                    
                    TransactionLog.objects.create(
                        transaction=trans,
                        status_from='processing',
                        status_to='failed',
                        reason='Insufficient balance'
                    )
                    
                    return f"Transfer {transaction_id} failed: insufficient balance"
            
            elif trans.transaction_type == 'deposit':
                wallet = Wallet.objects.get(user=trans.receiver, currency__code=trans.currency_code)
                wallet.balance += trans.amount
                wallet.save()
                
                trans.status = 'completed'
                trans.save()
                
                TransactionLog.objects.create(
                    transaction=trans,
                    status_from='processing',
                    status_to='completed',
                    reason='Deposit completed successfully'
                )
                
                update_financial_summaries.delay(trans.receiver.id)
                
                return f"Deposit {transaction_id} completed successfully"
            
            elif trans.transaction_type == 'withdrawal':
                wallet = Wallet.objects.get(user=trans.sender, currency__code=trans.currency_code)
                
                if wallet.balance >= trans.amount:
                    wallet.balance -= trans.amount
                    wallet.save()
                    
                    trans.status = 'completed'
                    trans.save()
                    
                    TransactionLog.objects.create(
                        transaction=trans,
                        status_from='processing',
                        status_to='completed',
                        reason='Withdrawal completed successfully'
                    )
                    
                    update_financial_summaries.delay(trans.sender.id)
                    
                    return f"Withdrawal {transaction_id} completed successfully"
                else:
                    trans.status = 'failed'
                    trans.save()
                    
                    TransactionLog.objects.create(
                        transaction=trans,
                        status_from='processing',
                        status_to='failed',
                        reason='Insufficient balance'
                    )
                    
                    return f"Withdrawal {transaction_id} failed: insufficient balance"
    
    except Exception as e:
        return f"Error processing transaction {transaction_id}: {str(e)}"


@shared_task
def update_financial_summaries(user_id):
    try:
        user = User.objects.get(id=user_id)
        summary, created = UserFinancialSummary.objects.get_or_create(user=user)
        
        total_balance = Wallet.objects.filter(user=user).aggregate(
            total=Sum('balance')
        )['total'] or Decimal('0.00')
        
        sent_transactions = Transaction.objects.filter(
            sender=user, status='completed'
        ).aggregate(
            total=Sum('amount'),
            count=Count('id'),
            fees=Sum('fee')
        )
        
        received_transactions = Transaction.objects.filter(
            receiver=user, status='completed'
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        summary.total_balance = total_balance
        summary.total_sent = sent_transactions['total'] or Decimal('0.00')
        summary.total_received = received_transactions['total'] or Decimal('0.00')
        summary.total_fees_paid = sent_transactions['fees'] or Decimal('0.00')
        summary.transaction_count = (sent_transactions['count'] or 0) + (received_transactions['count'] or 0)
        summary.save()
        
        return f"Updated financial summary for user {user_id}"
    
    except Exception as e:
        return f"Error updating financial summary for user {user_id}: {str(e)}"
