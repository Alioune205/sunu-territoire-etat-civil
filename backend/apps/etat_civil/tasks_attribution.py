"""
Tâches asynchrones et périodiques pour la gestion des attributions.
S'intègre avec Celery pour ne pas bloquer le thread principal.
"""
from celery import shared_task
from django.utils import timezone
from django.db import OperationalError
import logging

from apps.etat_civil.models_attribution import AttributionDossier, JournalAttribution, ProfilAgent
from apps.etat_civil.services.service_attribution import ServiceAttribution
from apps.dossiers.models import Dossier

logger = logging.getLogger(__name__)

# LE "GOD MOVE" RÉSILIENCE : Si la base est verrouillée par `select_for_update`, 
# Celery va réessayer automatiquement avec un délai exponentiel (Backoff)
@shared_task(bind=True, max_retries=5, default_retry_delay=2, autoretry_for=(OperationalError,))
def task_attribuer_dossier_async(self, dossier_id):
    """
    Tâche asynchrone pour attribuer un dossier en arrière-plan sans bloquer l'API.
    """
    try:
        dossier = Dossier.objects.get(id=dossier_id)
        resultat = ServiceAttribution.attribuer_dossier_automatiquement(dossier)
        if resultat is None:
            # Si le verrou a retourné None (déjà en cours par un autre processus)
            logger.info(f"Dossier {dossier_id} ignoré: verrouillage actif ou aucun agent.")
    except OperationalError as exc:
        logger.warning(f"Database lock sur le dossier {dossier_id}. Retry de la tâche Celery...")
        raise self.retry(exc=exc)
    except Dossier.DoesNotExist:
        logger.error(f"Impossible d'attribuer le dossier {dossier_id}: introuvable.")


@shared_task
def task_verifier_sla_et_escalader():
    """
    Tâche périodique (Cron Celery - ex: toutes les 15 mins).
    Vérifie toutes les attributions dont le SLA est dépassé et les escalade.
    """
    now = timezone.now()
    # Trouver toutes les attributions actives dont la date limite est dépassée
    attributions_en_retard = AttributionDossier.objects.filter(
        statut__in=[AttributionDossier.Status.ATTRIBUE, AttributionDossier.Status.EN_COURS],
        date_limite_sla__lt=now
    )

    for attribution in attributions_en_retard:
        # Escalade
        attribution.statut = AttributionDossier.Status.ESCALADE
        attribution.niveau_priorite = AttributionDossier.PriorityLevel.CRITIQUE
        attribution.save()

        # Audit
        JournalAttribution.objects.create(
            dossier=attribution.dossier,
            agent_concerne=attribution.agent,
            action=JournalAttribution.Action.ESCALADE_SLA,
            motif_detaille=f"SLA dépassé depuis {now - attribution.date_limite_sla}. Escalade automatique.",
        )
        logger.warning(f"Dossier {attribution.dossier.reference} escaladé (SLA dépassé).")

        # Optionnel : On pourrait relancer une réattribution automatique ici
        # task_attribuer_dossier_async.delay(attribution.dossier.id)

@shared_task
def task_recalculer_scores_agents():
    """
    Tâche périodique (Cron Celery - ex: chaque nuit).
    Recalcule le score global de tous les agents en fonction de leur historique de traitement.
    """
    agents = ProfilAgent.objects.all()
    for agent in agents:
        # Logique simplifiée : on augmente le score s'il a traité beaucoup de dossiers vite
        # Dans un vrai système ML, cela appellerait un modèle d'IA externe.
        if agent.dossiers_traites_historique > 100:
            agent.score_performance_global = min(100.0, agent.score_performance_global + 1.0)
        
        agent.save(update_fields=['score_performance_global'])
