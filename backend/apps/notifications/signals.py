from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.dossiers.models import Dossier
from .services import FCMService
from .models import Notification

@receiver(pre_save, sender=Dossier)
def dossier_status_change_notification(sender, instance, **kwargs):
    if not instance.pk:
        # New dossier
        if instance.status == Dossier.Status.SUBMITTED:
            FCMService.send_notification_to_user(
                user=instance.citizen,
                title="Dossier reçu",
                body=f"Votre dossier {instance.reference} a bien été reçu et enregistré.",
                notification_type=Notification.TypeChoices.SUCCESS,
                data={'dossier_id': str(instance.id)}
            )
        return

    try:
        old_instance = Dossier.objects.get(pk=instance.pk)
    except Dossier.DoesNotExist:
        return

    # Check for status changes
    if old_instance.status != instance.status:
        if instance.status == Dossier.Status.SUBMITTED:
            FCMService.send_notification_to_user(
                user=instance.citizen,
                title="Dossier reçu",
                body=f"Votre dossier {instance.reference} a bien été reçu et enregistré.",
                notification_type=Notification.TypeChoices.SUCCESS,
                data={'dossier_id': str(instance.id)}
            )
            
        elif instance.status == Dossier.Status.REJECTED:
            FCMService.send_notification_to_user(
                user=instance.citizen,
                title="Action requise sur votre dossier",
                body=f"Votre dossier {instance.reference} nécessite une action ou a été rejeté.",
                notification_type=Notification.TypeChoices.ACTION_REQUIRED,
                data={'dossier_id': str(instance.id)}
            )
            
        elif instance.status == Dossier.Status.COMPLETED:
            FCMService.send_notification_to_user(
                user=instance.citizen,
                title="Document disponible",
                body=f"Votre acte d'état civil (dossier {instance.reference}) est disponible !",
                notification_type=Notification.TypeChoices.SUCCESS,
                data={'dossier_id': str(instance.id)}
            )
            
        elif instance.status == Dossier.Status.IN_REVIEW and instance.assigned_agent:
            FCMService.send_notification_to_user(
                user=instance.assigned_agent,
                title="Nouveau dossier attribué",
                body=f"Le dossier {instance.reference} vous a été attribué pour traitement.",
                notification_type=Notification.TypeChoices.INFO,
                data={'dossier_id': str(instance.id)}
            )
