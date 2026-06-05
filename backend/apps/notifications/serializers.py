"""
Serializers for Notifications.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import NotificationToken, Notification

User = get_user_model()


class NotificationTokenSerializer(serializers.ModelSerializer):
    """Serializer for registering FCM tokens."""
    class Meta:
        model = NotificationToken
        fields = [
            'id',
            'token',
            'device_type',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Prevent token duplicates for the same user
        token = validated_data.get('token')
        existing = NotificationToken.objects.filter(token=token).first()
        if existing:
            existing.user = validated_data['user']
            existing.device_type = validated_data.get('device_type', existing.device_type)
            existing.is_active = True
            existing.save()
            return existing
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notification history entries."""
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'title',
            'body',
            'type',
            'type_display',
            'is_read',
            'data',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'title', 'body', 'type', 'type_display', 'data', 'created_at']


class SendNotificationSerializer(serializers.Serializer):
    """Serializer for manual/admin notification trigger."""
    user_id = serializers.UUIDField(required=True)
    title = serializers.CharField(max_length=255, required=True)
    body = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=Notification.Type.choices, required=True)
    data = serializers.JSONField(required=False, default=dict)

    def validate_user_id(self, value):
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("L'utilisateur spécifié n'existe pas.")
        return value
