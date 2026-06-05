"""
Dashboard views — API endpoints pour les statistiques et rapports du Dashboard administratif.
Accessible uniquement au personnel administratif (agents, admins).
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.shared.permissions import IsAdminStaff
from apps.shared.responses import success_response, error_response

from .services import DashboardStatsService
from .filters import DashboardFilterMixin
from .serializers import (
    OverviewStatsSerializer,
    DossierCountByStatusSerializer,
    DossierCountByTypeSerializer,
    DossierCountByCommuneSerializer,
    DailyVolumeSerializer,
    AgentPerformanceSerializer,
    RecentDossierSerializer,
    ProcessingDelaySerializer,
)


# =============================================================================
# Paramètres Swagger communs
# =============================================================================
COMMUNE_PARAM = OpenApiParameter(
    name='commune',
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.QUERY,
    description='ID de la commune (super_admin uniquement). Agents filtrés automatiquement.',
    required=False,
)
DAYS_PARAM = OpenApiParameter(
    name='days',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description='Nombre de jours pour le filtre temporel (défaut: 30, max: 365).',
    required=False,
)
LIMIT_PARAM = OpenApiParameter(
    name='limit',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description='Nombre max de résultats (défaut: 10, max: 100).',
    required=False,
)


class OverviewView(DashboardFilterMixin, APIView):
    """
    GET /api/dashboard/overview/
    Vue d'ensemble : totaux par statut, taux de complétion, délai moyen.
    """
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Vue d\'ensemble des statistiques',
        description='Retourne les statistiques globales : totaux, taux de complétion, délai moyen.',
        parameters=[COMMUNE_PARAM],
        responses={200: OverviewStatsSerializer},
    )
    def get(self, request):
        commune = self.get_commune_filter()
        data = DashboardStatsService.get_overview(commune=commune)
        return success_response(data=data, message='Statistiques globales récupérées.')


class CountByStatusView(DashboardFilterMixin, APIView):
    """
    GET /api/dashboard/by-status/
    Répartition des dossiers par statut.
    """
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Dossiers par statut',
        parameters=[COMMUNE_PARAM],
        responses={200: DossierCountByStatusSerializer(many=True)},
    )
    def get(self, request):
        commune = self.get_commune_filter()
        data = DashboardStatsService.get_count_by_status(commune=commune)
        return success_response(data=data)


class CountByTypeView(DashboardFilterMixin, APIView):
    """
    GET /api/dashboard/by-type/
    Répartition des dossiers par type (naissance, mariage, décès…).
    """
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Dossiers par type',
        parameters=[COMMUNE_PARAM],
        responses={200: DossierCountByTypeSerializer(many=True)},
    )
    def get(self, request):
        commune = self.get_commune_filter()
        data = DashboardStatsService.get_count_by_type(commune=commune)
        return success_response(data=data)


class CountByCommuneView(APIView):
    """
    GET /api/dashboard/by-commune/
    Répartition des dossiers par commune (super_admin uniquement).
    """
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Dossiers par commune',
        responses={200: DossierCountByCommuneSerializer(many=True)},
    )
    def get(self, request):
        if request.user.role != 'super_admin':
            return error_response(
                message='Seul le super administrateur peut voir les statistiques par commune.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
        data = DashboardStatsService.get_count_by_commune()
        return success_response(data=data)


class DailyVolumeView(DashboardFilterMixin, APIView):
    """
    GET /api/dashboard/daily-volume/
    Volume quotidien de dossiers créés sur les N derniers jours.
    """
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Volume quotidien',
        parameters=[COMMUNE_PARAM, DAYS_PARAM],
        responses={200: DailyVolumeSerializer(many=True)},
    )
    def get(self, request):
        commune = self.get_commune_filter()
        days = self.get_days_filter()
        data = DashboardStatsService.get_daily_volume(commune=commune, days=days)
        return success_response(data=data)


class AgentPerformanceView(DashboardFilterMixin, APIView):
    """
    GET /api/dashboard/agent-performance/
    Performance individuelle des agents (dossiers traités, délai moyen).
    """
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Performance des agents',
        parameters=[COMMUNE_PARAM],
        responses={200: AgentPerformanceSerializer(many=True)},
    )
    def get(self, request):
        commune = self.get_commune_filter()
        data = DashboardStatsService.get_agent_performance(commune=commune)
        return success_response(data=data)


class ProcessingDelaysView(DashboardFilterMixin, APIView):
    """
    GET /api/dashboard/processing-delays/
    Délais de traitement par type de dossier.
    """
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Délais de traitement',
        parameters=[COMMUNE_PARAM],
        responses={200: ProcessingDelaySerializer(many=True)},
    )
    def get(self, request):
        commune = self.get_commune_filter()
        data = DashboardStatsService.get_processing_delays(commune=commune)
        return success_response(data=data)


class RecentDossiersView(DashboardFilterMixin, APIView):
    """
    GET /api/dashboard/recent/
    Derniers dossiers soumis.
    """
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Dossiers récents',
        parameters=[COMMUNE_PARAM, LIMIT_PARAM],
        responses={200: RecentDossierSerializer(many=True)},
    )
    def get(self, request):
        commune = self.get_commune_filter()
        limit = self.get_limit_filter()
        data = DashboardStatsService.get_recent_dossiers(commune=commune, limit=limit)
        return success_response(data=data)


class StaleDossiersView(DashboardFilterMixin, APIView):
    """
    GET /api/dashboard/stale/
    Dossiers en attente depuis trop longtemps (alerte urgence).
    """
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Dossiers urgents en attente',
        parameters=[
            COMMUNE_PARAM,
            OpenApiParameter(
                name='hours',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Seuil en heures (défaut: 48).',
                required=False,
            ),
        ],
    )
    def get(self, request):
        commune = self.get_commune_filter()
        try:
            hours = int(request.query_params.get('hours', 48))
        except (ValueError, TypeError):
            hours = 48

        stale_qs = DashboardStatsService.get_stale_dossiers(commune=commune, stale_hours=hours)
        data = []
        for d in stale_qs[:50]:
            data.append({
                'id': str(d.id),
                'reference': d.reference,
                'type': d.type,
                'status': d.status,
                'citizen_name': d.citizen.full_name,
                'commune_name': d.commune.name,
                'agent_name': d.assigned_agent.full_name if d.assigned_agent else None,
                'submitted_at': d.submitted_at,
                'hours_waiting': round(
                    (timezone.now() - d.submitted_at).total_seconds() / 3600, 1
                ) if d.submitted_at else None,
            })
        return success_response(data=data, message=f'{len(data)} dossier(s) en attente depuis plus de {hours}h.')
