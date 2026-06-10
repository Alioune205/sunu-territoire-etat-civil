"""
URL configuration for System — Health check, métriques, logs.
"""
from django.urls import path
from .views import HealthCheckView, SystemMetricsView, SystemLogsView, SettingsView

app_name = 'system'

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('metrics/', SystemMetricsView.as_view(), name='metrics'),
    path('logs/', SystemLogsView.as_view(), name='logs'),
    path('settings/', SettingsView.as_view(), name='settings'),
]
