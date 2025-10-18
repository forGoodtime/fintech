"""
Health check and monitoring views
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time
import os


@never_cache
@require_http_methods(["GET"])
def health_check(request):
    """Basic health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'fintech-terminal',
        'version': getattr(settings, 'VERSION', '1.0.0')
    })


@never_cache
@require_http_methods(["GET"])
def health_detailed(request):
    """Detailed health check with dependencies"""
    health_data = {
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'fintech-terminal',
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'checks': {}
    }
    
    # Database check
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        health_data['checks']['database'] = {'status': 'healthy'}
    except Exception as e:
        health_data['status'] = 'unhealthy'
        health_data['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Cache check
    try:
        cache_key = 'health_check'
        cache.set(cache_key, 'test', 30)
        cache.get(cache_key)
        health_data['checks']['cache'] = {'status': 'healthy'}
    except Exception as e:
        health_data['status'] = 'unhealthy'
        health_data['checks']['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Disk space check
    try:
        disk_usage = os.statvfs('/')
        available_space = disk_usage.f_frsize * disk_usage.f_bavail
        total_space = disk_usage.f_frsize * disk_usage.f_blocks
        used_percentage = ((total_space - available_space) / total_space) * 100
        
        if used_percentage < 90:
            health_data['checks']['disk'] = {
                'status': 'healthy',
                'used_percentage': used_percentage
            }
        else:
            health_data['status'] = 'unhealthy'
            health_data['checks']['disk'] = {
                'status': 'unhealthy',
                'used_percentage': used_percentage,
                'error': 'Disk usage too high'
            }
    except Exception as e:
        health_data['checks']['disk'] = {
            'status': 'unknown',
            'error': str(e)
        }
    
    return JsonResponse(health_data)


@never_cache
@require_http_methods(["GET"])
def readiness_check(request):
    """Readiness probe for Kubernetes/Docker"""
    try:
        # Check if we can connect to database
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        
        # Check if migrations are up to date
        from django.core.management import execute_from_command_line
        from django.core.management.base import BaseCommand
        from io import StringIO
        import sys
        
        return JsonResponse({
            'status': 'ready',
            'timestamp': time.time()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': time.time()
        }, status=503)


@never_cache
@require_http_methods(["GET"])
def liveness_check(request):
    """Liveness probe - simple check that service is running"""
    return JsonResponse({
        'status': 'alive',
        'timestamp': time.time()
    })


@never_cache
@require_http_methods(["GET"])
def metrics_info(request):
    """Basic metrics information"""
    from django.contrib.auth import get_user_model
    from wallets.models import Wallet
    from transactions.models import Transaction
    
    User = get_user_model()
    
    try:
        metrics = {
            'users_total': User.objects.count(),
            'users_active': User.objects.filter(is_active=True).count(),
            'wallets_total': Wallet.objects.count(),
            'wallets_active': Wallet.objects.filter(is_active=True).count(),
            'transactions_total': Transaction.objects.count(),
            'transactions_completed': Transaction.objects.filter(status='completed').count(),
            'timestamp': time.time()
        }
        return JsonResponse(metrics)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'timestamp': time.time()
        }, status=500)
