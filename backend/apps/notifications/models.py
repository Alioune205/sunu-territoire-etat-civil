"""
Notifications models for FCM tokens and notification history.
"""
from django.conf import settings
from django.db import models
from apps.shared.models import TimeStampedModel


class NotificationToken(TimeStampedModel):
    """
    Stores FCM registration tokens for devices associated with users.
    """
    class DeviceType(models.TextChoices):
        ANDROID = 'android', 'Android'
        IOS = 'ios', 'iOS'
        WEB = 'web', 'Web'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_tokens',
        verbose_name='Utilisateur',
    )
    token = models.CharField(
        max_length=500,
        unique=True,
        verbose_name='Token FCM',
    )
    device_type = models.CharField(
        max_length=15,
        choices=DeviceType.choices,
        default=DeviceType.WEB,
        verbose_name='Type d\'appareil',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Actif',
    )

    class Meta:
        verbose_name = 'Token de notification'
        verbose_name_plural = 'Tokens de notification'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f'{self.user.email} — {self.device_type} ({self.token[:20]}...)'


class Notification(TimeStampedModel):
    """
    Stores history of sent notifications.
    """
    class Type(models.TextChoices):
        # Citoyen notifications
        DOSSIER_SUBMITTED = 'dossier_submitted', 'Dossier reçu'
        DOSSIER_APPROVED = 'dossier_approved', 'Dossier validé'
        DOSSIER_REJECTED = 'dossier_rejected', 'Dossier rejeté'
        DOCUMENT_AVAILABLE = 'document_available', 'Document disponible'
        
        # Agent notifications
        NEW_DOSSIER = 'new_dossier', 'Nouveau dossier'
        URGENT_DOSSIER = 'urgent_dossier', 'Dossier urgent'
        ACTION_REQUIRED = 'action_required', 'Action requise'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinataire',
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Titre',
    )
    body = models.TextField(
        verbose_name='Contenu',
    )
    type = models.CharField(
        max_length=30,
        choices=Type.choices,
        verbose_name='Type de notification',
        db_index=True,
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Lu',
        db_index=True,
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Données additionnelles',
    )

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['type']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.title} -> {self.user.email} ({self.created_at})'
