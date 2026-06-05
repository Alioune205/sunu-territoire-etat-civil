"""
URL configuration for Notifications.
# TODO: DEV 2 — Implement URLs here
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FCMDeviceViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'devices', FCMDeviceViewSet, basename='device')
router.register(r'', NotificationViewSet, basename='notification')

app_name = 'notifications'

urlpatterns = [
    path('', include(router.urls)),
]
