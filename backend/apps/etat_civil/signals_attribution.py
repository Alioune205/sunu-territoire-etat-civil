"""
Signaux Django pour brancher le moteur de répartition au cycle de vie naturel des dossiers.
C'est ici qu'Alioune et vous faites la jonction sans vous marcher sur les pieds.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

from apps.dossiers.models import Dossier
from apps.etat_civil.tasks_attribution import task_attribuer_dossier_async

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Dossier)
def declencher_attribution_sur_nouveau_dossier(sender, instance, created, **kwargs):
    """
    Dès qu'un dossier est créé ou soumis (passe de DRAFT à SUBMITTED),
    ce signal intercepte l'événement et lance le moteur d'attribution en tâche de fond.
    """
    if created and instance.status == Dossier.Status.SUBMITTED:
        # Si le dossier est créé directement avec le statut SOUMIS
        logger.info(f"Signal: Nouveau dossier {instance.reference} soumis. Déclenchement de l'attribution asynchrone.")
        task_attribuer_dossier_async.delay(instance.id)
    
    elif not created:
        # Si le dossier existait (Brouillon) et vient d'être passé à SOUMIS
        # On vérifie s'il n'a pas déjà d'agent
        if instance.status == Dossier.Status.SUBMITTED and not instance.assigned_agent:
            # Pour éviter les boucles infinies avec les sauvegardes, on s'assure qu'il n'a pas déjà une attribution
            attribution_existante = getattr(instance, 'attributions_historique', None)
            if not attribution_existante or not attribution_existante.exists():
                logger.info(f"Signal: Dossier {instance.reference} mis à jour vers SOUMIS. Déclenchement de l'attribution.")
                task_attribuer_dossier_async.delay(instance.id)
