"""
Notifications models.
# TODO: DEV 2 — Implement Notification models here
"""
from django.db import models
from django.conf import settings
from apps.shared.models import TimeStampedModel

class FCMDevice(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fcm_devices')
    registration_id = models.CharField(max_length=255, unique=True, verbose_name="Token FCM")
    device_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID de l'appareil")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Appareil FCM"
        verbose_name_plural = "Appareils FCM"

    def __str__(self):
        return f"{self.user.email if hasattr(self.user, 'email') else self.user} - {self.registration_id[:10]}..."

class Notification(TimeStampedModel):
    class TypeChoices(models.TextChoices):
        INFO = 'INFO', 'Information'
        ACTION_REQUIRED = 'ACTION', 'Action requise'
        SUCCESS = 'SUCCESS', 'Succès'
        ALERT = 'ALERT', 'Alerte'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    body = models.TextField()
    notification_type = models.CharField(max_length=10, choices=TypeChoices.choices, default=TypeChoices.INFO)
    data = models.JSONField(blank=True, null=True, help_text="Données additionnelles pour deep linking")
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user}"
