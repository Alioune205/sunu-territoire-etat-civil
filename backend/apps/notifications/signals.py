"""
Notifications signals — Déclenchement automatique des notifications
et invalidation du cache dashboard lors des changements de statut des dossiers.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.dossiers.models import Dossier
from .services import FCMService
from .models import Notification

logger = logging.getLogger('system')


@receiver(pre_save, sender=Dossier)
def capture_old_status(sender, instance, **kwargs):
    """
    Capture l'ancien statut avant la sauvegarde pour pouvoir 
    envoyer la notification dans le post_save en toute sécurité.
    Correction d'audit : Ne pas envoyer de push si la sauvegarde échoue.
    """
    if instance.pk:
        try:
            old_instance = Dossier.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Dossier.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Dossier)
def dossier_status_change_notification(sender, instance, created, **kwargs):
    """
    Envoie une notification FCM au citoyen/agent quand le statut d'un dossier change.
    Utilise `post_save` pour garantir que la donnée est commitée en base.
    """
    if created:
        # Nouveau dossier — notifier uniquement si soumis directement
        if instance.status == Dossier.Status.SUBMITTED:
            FCMService.send_notification_to_user(
                user=instance.citizen,
                title="Dossier reçu",
                body=f"Votre dossier {instance.reference} a bien été reçu et enregistré.",
                notification_type=Notification.Type.UPDATE,
                data={'dossier_id': str(instance.id)}
            )
        return

    old_status = getattr(instance, '_old_status', None)

    # Pas de changement de statut → rien à faire
    if old_status == instance.status:
        return

    # ── Notifications selon le nouveau statut ──

    if instance.status == Dossier.Status.SUBMITTED:
        FCMService.send_notification_to_user(
            user=instance.citizen,
            title="Dossier reçu",
            body=f"Votre dossier {instance.reference} a bien été reçu et enregistré.",
            notification_type=Notification.Type.UPDATE,
            data={'dossier_id': str(instance.id)}
        )

    elif instance.status == Dossier.Status.IN_REVIEW and instance.assigned_agent:
        # Notifier l'agent assigné
        FCMService.send_notification_to_user(
            user=instance.assigned_agent,
            title="Nouveau dossier attribué",
            body=f"Le dossier {instance.reference} vous a été attribué pour traitement.",
            notification_type=Notification.Type.INFO,
            data={'dossier_id': str(instance.id)}
        )
        # Notifier le citoyen que son dossier est en cours de traitement
        FCMService.send_notification_to_user(
            user=instance.citizen,
            title="Dossier en cours de traitement",
            body=f"Votre dossier {instance.reference} est en cours d'examen par un agent.",
            notification_type=Notification.Type.INFO,
            data={'dossier_id': str(instance.id)}
        )

    elif instance.status == Dossier.Status.APPROVED:
        FCMService.send_notification_to_user(
            user=instance.citizen,
            title="Dossier approuvé ✅",
            body=f"Votre dossier {instance.reference} a été approuvé ! Il sera finalisé prochainement.",
            notification_type=Notification.Type.UPDATE,
            data={'dossier_id': str(instance.id)}
        )

    elif instance.status == Dossier.Status.REJECTED:
        FCMService.send_notification_to_user(
            user=instance.citizen,
            title="Action requise sur votre dossier",
            body=f"Votre dossier {instance.reference} nécessite une action ou a été rejeté.",
            notification_type=Notification.Type.WARNING,
            data={'dossier_id': str(instance.id)}
        )

    elif instance.status == Dossier.Status.COMPLETED:
        FCMService.send_notification_to_user(
            user=instance.citizen,
            title="Document disponible 🎉",
            body=f"Votre acte d'état civil (dossier {instance.reference}) est disponible !",
            notification_type=Notification.Type.UPDATE,
            data={'dossier_id': str(instance.id)}
        )


@receiver(post_save, sender=Dossier)
def invalidate_dashboard_cache_on_dossier_change(sender, instance, **kwargs):
    """
    Invalide automatiquement le cache du dashboard à chaque modification de dossier.
    Garantit que les statistiques sont toujours à jour sans délai incohérent.
    """
    try:
        from apps.dashboard.services import invalidate_dashboard_cache
        invalidate_dashboard_cache()
    except Exception as e:
        logger.warning(f'[Signals] Erreur lors de l\'invalidation du cache dashboard : {e}')
