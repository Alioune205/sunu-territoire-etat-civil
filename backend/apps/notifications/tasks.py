"""
Notifications tasks — Tâches automatisées pour les notifications.
Peut être exécuté via management commands ou Celery si configuré.
"""
import logging
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.dossiers.models import Dossier
from .services import FCMService
from .models import Notification

logger = logging.getLogger('system')
User = get_user_model()


def send_stale_dossier_alerts(stale_hours=48):
    """
    Envoie des alertes aux agents pour les dossiers en attente depuis trop longtemps.
    À appeler périodiquement (cron ou Celery beat).

    Args:
        stale_hours: Nombre d'heures sans action avant alerte (défaut: 48).
    """
    threshold = timezone.now() - timedelta(hours=stale_hours)

    stale_dossiers = Dossier.objects.filter(
        status__in=[Dossier.Status.SUBMITTED, Dossier.Status.IN_REVIEW],
        submitted_at__lte=threshold,
    ).select_related('assigned_agent', 'citizen', 'commune')

    count = stale_dossiers.count()
    if count == 0:
        logger.info('[Tasks] Aucun dossier en attente dépassant le seuil.')
        return 0

    logger.info(f'[Tasks] {count} dossier(s) en attente depuis plus de {stale_hours}h.')

    notified_agents = set()
    for dossier in stale_dossiers:
        # Notifier l'agent assigné s'il existe
        if dossier.assigned_agent and dossier.assigned_agent.id not in notified_agents:
            FCMService.send_notification_to_user(
                user=dossier.assigned_agent,
                title='⚠️ Alerte de dossier urgent',
                body=(
                    f'Le dossier {dossier.reference} est en attente depuis plus de {stale_hours}h. '
                    f'Citoyen : {dossier.citizen.full_name}.'
                ),
                notification_type=Notification.TypeChoices.ALERT,
                data={
                    'dossier_id': str(dossier.id),
                    'reference': dossier.reference,
                    'action': 'stale_alert',
                },
            )
            notified_agents.add(dossier.assigned_agent.id)

    logger.info(f'[Tasks] Alertes envoyées à {len(notified_agents)} agent(s).')
    return len(notified_agents)


def send_daily_summary_to_admins():
    """
    Envoie un résumé quotidien aux administrateurs :
    nombre de dossiers reçus, traités, en attente.
    """
    now = timezone.now()
    yesterday = now - timedelta(days=1)

    received = Dossier.objects.filter(submitted_at__gte=yesterday).count()
    completed = Dossier.objects.filter(completed_at__gte=yesterday).count()
    pending = Dossier.objects.filter(
        status__in=[Dossier.Status.SUBMITTED, Dossier.Status.IN_REVIEW]
    ).count()

    admins = User.objects.filter(
        role__in=['civil_admin', 'super_admin'],
        is_active=True,
    )

    for admin in admins:
        FCMService.send_notification_to_user(
            user=admin,
            title='📊 Résumé quotidien',
            body=(
                f'Dernières 24h : {received} dossier(s) reçu(s), '
                f'{completed} traité(s). '
                f'{pending} dossier(s) en attente au total.'
            ),
            notification_type=Notification.TypeChoices.INFO,
            data={'action': 'daily_summary'},
        )

    logger.info(f'[Tasks] Résumé quotidien envoyé à {admins.count()} administrateur(s).')
    return admins.count()


def cleanup_old_notifications(days=90):
    """
    Supprime les notifications lues de plus de N jours.
    Évite l'accumulation en base de données.
    """
    threshold = timezone.now() - timedelta(days=days)
    deleted, _ = Notification.objects.filter(
        is_read=True,
        created_at__lte=threshold,
    ).delete()

    logger.info(f'[Tasks] {deleted} notification(s) lue(s) de plus de {days} jours supprimée(s).')
    return deleted


def notify_citizen_dossier_reminder():
    """
    Rappelle aux citoyens que leur dossier en brouillon n'a pas été soumis.
    Cible les dossiers en brouillon créés il y a plus de 3 jours.
    """
    threshold = timezone.now() - timedelta(days=3)

    draft_dossiers = Dossier.objects.filter(
        status=Dossier.Status.DRAFT,
        created_at__lte=threshold,
    ).select_related('citizen')

    notified = 0
    for dossier in draft_dossiers:
        FCMService.send_notification_to_user(
            user=dossier.citizen,
            title='📝 Rappel : dossier non soumis',
            body=(
                f'Votre dossier {dossier.reference} est toujours en brouillon. '
                f'N\'oubliez pas de le soumettre pour qu\'il soit traité.'
            ),
            notification_type=Notification.TypeChoices.INFO,
            data={
                'dossier_id': str(dossier.id),
                'action': 'draft_reminder',
            },
        )
        notified += 1

    logger.info(f'[Tasks] Rappels envoyés à {notified} citoyen(s) pour dossiers en brouillon.')
    return notified
