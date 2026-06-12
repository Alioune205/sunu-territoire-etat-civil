from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Count
from django.shortcuts import get_object_or_404
from apps.etat_civil.models_attribution import ProfilAgent, AttributionDossier, JournalAttribution
from apps.etat_civil.services.service_attribution import ServiceAttribution
from apps.etat_civil.services.moteur_scoring import MoteurScoring
from apps.dossiers.models import Dossier
from apps.users.models import User
from apps.shared.pagination import StandardPagination

class StatsAttributionView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        total = Dossier.objects.count()
        en_attente = Dossier.objects.filter(status='soumis').count()
        en_traitement = Dossier.objects.filter(status='in_review').count()
        termines = Dossier.objects.filter(status='termine').count()
        rejetes = Dossier.objects.filter(status='rejete').count()

        return Response({
            'total': total,
            'en_attente': en_attente,
            'en_traitement': en_traitement,
            'termines': termines,
            'rejetes': rejetes
        })

class AgentsChargeView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        agents = ProfilAgent.objects.filter(user__is_active=True).select_related('user')
        data = []
        for agent in agents:
            en_cours = AttributionDossier.objects.filter(agent_actuel=agent.user, dossier__status='in_review').count()
            data.append({
                'id': agent.user.id,
                'email': agent.user.email,
                'nom': agent.user.get_full_name(),
                'score_global': agent.score_global,
                'charge_maximale': agent.charge_maximale,
                'dossiers_en_cours': en_cours,
                'disponibilite': agent.disponibilite
            })
        return Response(data)

class CarteAttributionView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    pagination_class = StandardPagination

    def get(self, request):
        queryset = AttributionDossier.objects.filter(dossier__status='in_review').select_related('dossier', 'agent_actuel').order_by('-date_attribution')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        data = []
        for attr in page:
            data.append({
                'id': attr.id,
                'dossier_id': attr.dossier.id,
                'dossier_type': getattr(attr.dossier, 'type', 'inconnu'),
                'agent_email': attr.agent_actuel.email,
                'score': attr.score_attribution,
                'priorite': attr.niveau_priorite,
                'justification_ia': attr.justification_ia,
                'date_attribution': attr.date_attribution
            })
        return paginator.get_paginated_response(data)

class JournalAttributionView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    pagination_class = StandardPagination

    def get(self, request):
        queryset = JournalAttribution.objects.all().order_by('-timestamp')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        data = []
        for log in page:
            data.append({
                'id': log.id,
                'timestamp': log.timestamp,
                'action': log.libelle_action,
                'dossier_id': log.dossier_id,
                'agent_avant': log.agent_avant,
                'agent_apres': log.agent_apres,
                'score': log.score_calcule,
                'responsable': log.responsable.email if log.responsable else 'Système'
            })
        return paginator.get_paginated_response(data)

class ReattribuerDossierView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request, dossier_id):
        dossier = get_object_or_404(Dossier, id=dossier_id)
        nouvel_agent_id = request.data.get('agent_id')
        raison = request.data.get('raison')

        if not nouvel_agent_id or not raison:
            return Response({"error": "agent_id et raison sont requis."}, status=status.HTTP_400_BAD_REQUEST)

        nouvel_agent = get_object_or_404(User, id=nouvel_agent_id)
        service = ServiceAttribution()
        attribution, message = service.reattribuer(
            dossier=dossier,
            nouvel_agent_user=nouvel_agent,
            source='superviseur',
            responsable=request.user,
            justification_manuelle=raison
        )

        if attribution:
            return Response({"message": message})
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

class SuspendreAttributionView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request):
        commune_id = request.data.get('commune_id')
        duree = int(request.data.get('duree_heures', 24))
        if not commune_id:
            return Response({"error": "commune_id requis."}, status=status.HTTP_400_BAD_REQUEST)
        
        service = ServiceAttribution()
        msg = service.suspendre_attribution_auto(commune_id, duree)
        return Response({"message": msg})

class AgentPerformanceView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, agent_id):
        agent = get_object_or_404(ProfilAgent, user__id=agent_id)
        return Response({
            'score_global': agent.score_global,
            'temps_moyen': agent.temps_moyen_traitement,
            'taux_reussite': agent.taux_reussite,
            'taux_respect_delais': agent.taux_respect_delais
        })

class RecommandationAgentView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, dossier_id):
        dossier = get_object_or_404(Dossier, id=dossier_id)
        moteur = MoteurScoring()
        agents = ProfilAgent.objects.filter(user__is_active=True, disponibilite=True)
        
        scores = []
        for agent in agents:
            res = moteur.calculer_score_agent(agent, dossier)
            scores.append({
                'agent_id': agent.user.id,
                'email': agent.user.email,
                'score': res['score_total'],
                'details': res['details'],
                'justification': moteur._generer_justification(agent, res)
            })
        
        scores.sort(key=lambda x: x['score'], reverse=True)
        return Response(scores[:3])
