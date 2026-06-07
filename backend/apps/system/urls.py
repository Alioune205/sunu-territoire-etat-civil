from django.urls import path
from .views import SystemHealthView, SystemLogsView, SystemActivityView

urlpatterns = [
    path('health/', SystemHealthView.as_view(), name='system-health'),
    path('logs/', SystemLogsView.as_view(), name='system-logs'),
    path('activity/', SystemActivityView.as_view(), name='system-activity'),
]
