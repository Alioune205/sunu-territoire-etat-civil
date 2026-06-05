"""
URL configuration for Notifications.
"""
from django.urls import path
from .views import NotificationViewSet

urlpatterns = [
    path('send/', NotificationViewSet.as_view({'post': 'send_notification'}), name='notification-send'),
    path('history/', NotificationViewSet.as_view({'get': 'list'}), name='notification-history'),
    path('tokens/', NotificationViewSet.as_view({'post': 'register_token'}), name='notification-token-register'),
    path('<uuid:pk>/read/', NotificationViewSet.as_view({'post': 'mark_as_read'}), name='notification-read'),
    path('read-all/', NotificationViewSet.as_view({'post': 'mark_all_as_read'}), name='notification-read-all'),
]
