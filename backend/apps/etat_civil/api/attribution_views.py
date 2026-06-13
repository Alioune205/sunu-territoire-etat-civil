"""
Vues (Endpoints) REST pour l'API du module de répartition intelligente.
Permet au Frontend de consulter les charges et déclencher des réattributions.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from apps.etat_civil.models_attribution import ProfilAgent, AttributionDossier
from apps.etat_civil.services.service_attribution import ServiceAttribution
from apps.dossiers.models import Dossier

# Pour un vrai projet, il faudrait créer des serializers complets (ex: ProfilAgentSerializer).
# Ici on simplifie les endpoints métiers pour le Hackathon.

class AttributionViewSet(viewsets.ViewSet):
    """
    Endpoints spécifiques pour la gestion des attributions.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='forcer-attribution/(?P<dossier_id>[^/.]+)')
    def forcer_attribution(self, request, dossier_id=None):
        """
        Force le moteur à ré-attribuer un dossier spécifique (ex: si l'agent précédent est tombé malade).
        """
        try:
            dossier = Dossier.objects.get(id=dossier_id)
        except Dossier.DoesNotExist:
            return Response({"error": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # On appelle le service d'orchestration de manière synchrone pour avoir le résultat immédiat
        nouvelle_attribution = ServiceAttribution.attribuer_dossier_automatiquement(dossier)

        if nouvelle_attribution:
            return Response({
                "message": "Dossier attribué avec succès.",
                "agent": nouvelle_attribution.agent.user.full_name,
                "score_matching": nouvelle_attribution.score_matching_initial,
                "priorite": nouvelle_attribution.get_niveau_priorite_display(),
                "limite_sla": nouvelle_attribution.date_limite_sla
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Aucun agent disponible pour le moment. Le dossier reste en file d'attente."
            }, status=status.HTTP_409_CONFLICT)

    # OPTIMISATION REDIS : Le Dashboard du Maire peut être requêté souvent.
    # On met le résultat en cache pendant 30 secondes pour soulager la base PostgreSQL.
    @method_decorator(cache_page(30))
    @action(detail=False, methods=['get'], url_path='monitoring-agents')
    def monitoring_agents(self, request):
        """
        Endpoint pour le Dashboard du Maire (DEV 2A).
        Affiche en temps réel la charge de tous les agents de la commune avec Cache Redis.
        """
        commune = request.user.commune
        if not commune:
            return Response({"error": "Vous n'êtes assigné à aucune commune."}, status=status.HTTP_403_FORBIDDEN)

        # On refait l'optimisation N+1 ici aussi pour l'API !
        from django.db.models import Count, Q
        agents = ProfilAgent.objects.filter(user__commune=commune).annotate(
            charge_calculee=Count('attributions', filter=Q(attributions__statut='en_cours'))
        ).select_related('user')
        
        data = []
        for agent in agents:
            data.append({
                "agent_id": agent.id,
                "nom_complet": agent.user.full_name,
                "statut": agent.get_statut_actuel_display(),
                "charge_actuelle": agent.charge_calculee,
                "capacite_maximale": agent.capacite_maximale,
                "score_performance": agent.score_performance_global,
                "est_disponible": agent.est_disponible
            })

        return Response({"agents_metrics": data}, status=status.HTTP_200_OK)
