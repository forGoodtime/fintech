from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('health/detailed/', views.health_detailed, name='health_detailed'),
    path('ready/', views.readiness_check, name='readiness_check'),
    path('alive/', views.liveness_check, name='liveness_check'),
    path('metrics/', views.metrics_info, name='metrics_info'),
]
