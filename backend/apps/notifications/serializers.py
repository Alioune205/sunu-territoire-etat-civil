"""
Serializers for the Notifications app.
"""
from rest_framework import serializers
from .models import Notification, DeviceToken


class NotificationSerializer(serializers.ModelSerializer):
    """Sérialiseur complet d'une notification."""

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message',
            'notification_type', 'channel', 'data',
            'is_read', 'delivered_at', 'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'delivered_at']


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'enregistrement d'un token FCM."""

    class Meta:
        model = DeviceToken
        fields = ['id', 'token', 'device_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
