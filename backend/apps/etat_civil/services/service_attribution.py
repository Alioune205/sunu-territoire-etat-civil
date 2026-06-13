"""
Service d'Attribution - Orchestrateur (Facade) combinant le Scoring et la Priorité.
"""
from django.db import transaction, OperationalError
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging

from apps.dossiers.models import Dossier
from apps.etat_civil.models_attribution import ProfilAgent, AttributionDossier, JournalAttribution
from .moteur_scoring import MoteurScoring
from .moteur_priorite import MoteurPriorite

logger = logging.getLogger(__name__)

class ServiceAttribution:
    """
    Façade d'orchestration. C'est ce service qui est appelé par les vues (API) 
    ou par les signaux lors de la création d'un dossier.
    Garantit l'atomicité des transactions de base de données (ACID).
    """

    @classmethod
    @transaction.atomic
    def attribuer_dossier_automatiquement(cls, dossier_instance: Dossier) -> AttributionDossier:
        """
        Tente d'attribuer un dossier au meilleur agent disponible.
        Retourne l'objet AttributionDossier créé (ou None si aucun agent dispo).
        """
        # SÉCURITÉ EXTRÊME (Pessimistic Locking) : Verrouiller la ligne SQL pour empêcher 
        # les "Race Conditions". On laisse la DatabaseError remonter pour le Retry de Celery.
        try:
            dossier = Dossier.objects.select_for_update(nowait=True).get(id=dossier_instance.id)
        except OperationalError:
            # On relance l'erreur pour que Celery déclenche le Backoff Automatique
            raise OperationalError(f"Dossier {dossier_instance.id} verrouillé.")
        except Exception as e:
            logger.warning(f"Erreur inattendue sur {dossier_instance.reference} : {str(e)}")
            return None

        # 1. Sécurité : Vérifier si le dossier a déjà une attribution active
        attribution_existante = getattr(dossier, 'attribution_active', None)
        if attribution_existante and attribution_existante.statut in [AttributionDossier.Status.ATTRIBUE, AttributionDossier.Status.EN_COURS]:
            logger.warning(f"Le dossier {dossier.reference} a déjà une attribution active.")
            return attribution_existante

        # 2. Chercher le meilleur agent
        meilleur_agent, score = MoteurScoring.trouver_meilleur_agent(dossier)

        if not meilleur_agent:
            # Aucun agent n'est disponible. Le dossier reste en file d'attente (Non assigné).
            logger.info(f"Aucun agent disponible pour le dossier {dossier.reference}.")
            return None

        # 3. Calculer les métriques
        priorite = MoteurPriorite.calculer_priorite(dossier)
        date_sla = MoteurPriorite.calculer_date_limite_sla(dossier)

        # 4. Créer l'attribution
        # La sauvegarde de cette instance va automatiquement synchroniser le Dossier d'Alioune grâce à notre surcharge save()
        nouvelle_attribution = AttributionDossier.objects.create(
            dossier=dossier,
            agent=meilleur_agent,
            statut=AttributionDossier.Status.ATTRIBUE,
            niveau_priorite=priorite,
            date_limite_sla=date_sla,
            score_matching_initial=score
        )

        # 5. Créer la trace d'audit (Journal) indestructible
        JournalAttribution.objects.create(
            dossier=dossier,
            agent_concerne=meilleur_agent,
            action=JournalAttribution.Action.ATTRIBUTION_AUTOMATIQUE if not attribution_existante else JournalAttribution.Action.REATTRIBUTION_AUTOMATIQUE,
            motif_detaille=f"Attribué via Moteur de Scoring. Score: {score}. Priorité: {priorite}.",
            anciennes_valeurs={}
        )

        logger.info(f"Dossier {dossier.reference} attribué avec succès à {meilleur_agent.user.last_name} (Score: {score}).")
        
        # L'ULTIME GOD MOVE : Le Push Temps Réel (WebSockets)
        # On informe le Frontend de l'agent instantanément pour qu'il voie le dossier apparaître 
        # sans avoir à rafraîchir la page !
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"agent_{meilleur_agent.user.id}",
                    {
                        "type": "nouvelle_attribution",
                        "dossier_reference": dossier.reference,
                        "priorite": nouvelle_attribution.get_niveau_priorite_display(),
                        "message": "Nouveau dossier attribué"
                    }
                )
        except Exception as e:
            logger.error(f"Échec de notification WebSocket pour l'agent {meilleur_agent.user.id} : {e}")

        return nouvelle_attribution

    @classmethod
    @transaction.atomic
    def clore_attribution(cls, dossier: Dossier, agent: ProfilAgent):
        """
        Appelé quand un agent a fini de traiter un dossier (Validé ou Rejeté).
        """
        try:
            attribution = AttributionDossier.objects.get(
                dossier=dossier, 
                agent=agent, 
                statut__in=[AttributionDossier.Status.ATTRIBUE, AttributionDossier.Status.EN_COURS]
            )
            attribution.statut = AttributionDossier.Status.TERMINE
            attribution.date_traitement_effectif = timezone.now()
            attribution.save()

            JournalAttribution.objects.create(
                dossier=dossier,
                agent_concerne=agent,
                action=JournalAttribution.Action.CHANGEMENT_STATUT,
                motif_detaille="Clôture de l'attribution suite au traitement du dossier."
            )
        except AttributionDossier.DoesNotExist:
            pass
