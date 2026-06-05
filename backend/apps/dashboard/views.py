"""
Dashboard views — API endpoints pour les statistiques et rapports.
Inclut l'Export CSV, la mise en cache et l'audit d'export.
"""
import csv
import logging
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.shared.permissions import IsAdminStaff
from apps.shared.responses import success_response, error_response
from apps.dossiers.models import Dossier

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

logger = logging.getLogger('system')

# ── Paramètres Swagger réutilisables ──
COMMUNE_PARAM = OpenApiParameter(
    name='commune', type=OpenApiTypes.UUID,
    location=OpenApiParameter.QUERY, required=False,
    description='UUID de la commune pour filtrer les résultats.',
)
DAYS_PARAM = OpenApiParameter(
    name='days', type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY, required=False,
    description='Nombre de jours (1-365, défaut: 30).',
)
LIMIT_PARAM = OpenApiParameter(
    name='limit', type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY, required=False,
    description='Nombre maximum de résultats (1-100, défaut: 10).',
)


# =============================================================================
# ENDPOINTS DASHBOARD
# =============================================================================

class OverviewView(DashboardFilterMixin, APIView):
    """Vue d'ensemble des statistiques globales avec cache."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Vue d\'ensemble avec Cache',
        parameters=[COMMUNE_PARAM],
        responses={200: OverviewStatsSerializer},
    )
    def get(self, request):
        commune = self.get_commune_filter()
        data = DashboardStatsService.get_overview(commune=commune)
        return success_response(data=data)


class CountByStatusView(DashboardFilterMixin, APIView):
    """Nombre de dossiers par statut."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Répartition par statut',
        parameters=[COMMUNE_PARAM],
        responses={200: DossierCountByStatusSerializer(many=True)},
    )
    def get(self, request):
        data = DashboardStatsService.get_count_by_status(commune=self.get_commune_filter())
        return success_response(data=data)


class CountByTypeView(DashboardFilterMixin, APIView):
    """Nombre de dossiers par type d'acte."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Répartition par type d\'acte',
        parameters=[COMMUNE_PARAM],
        responses={200: DossierCountByTypeSerializer(many=True)},
    )
    def get(self, request):
        data = DashboardStatsService.get_count_by_type(commune=self.get_commune_filter())
        return success_response(data=data)


class CountByCommuneView(APIView):
    """Nombre de dossiers par commune — super_admin uniquement."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Répartition par commune (super admin)',
        responses={200: DossierCountByCommuneSerializer(many=True)},
    )
    def get(self, request):
        if request.user.role != 'super_admin':
            return error_response(message='Réservé au super administrateur.', status_code=403)
        return success_response(data=DashboardStatsService.get_count_by_commune())


class DailyVolumeView(DashboardFilterMixin, APIView):
    """Volume quotidien de dossiers."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Volume quotidien',
        parameters=[COMMUNE_PARAM, DAYS_PARAM],
        responses={200: DailyVolumeSerializer(many=True)},
    )
    def get(self, request):
        data = DashboardStatsService.get_daily_volume(
            commune=self.get_commune_filter(),
            days=self.get_days_filter(),
        )
        return success_response(data=data)


class AgentPerformanceView(DashboardFilterMixin, APIView):
    """Performance des agents — classement par dossiers traités."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Performance des agents',
        parameters=[COMMUNE_PARAM],
        responses={200: AgentPerformanceSerializer(many=True)},
    )
    def get(self, request):
        data = DashboardStatsService.get_agent_performance(commune=self.get_commune_filter())
        return success_response(data=data)


class ProcessingDelaysView(DashboardFilterMixin, APIView):
    """Délais de traitement par type de dossier."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Délais de traitement',
        parameters=[COMMUNE_PARAM],
        responses={200: ProcessingDelaySerializer(many=True)},
    )
    def get(self, request):
        data = DashboardStatsService.get_processing_delays(commune=self.get_commune_filter())
        return success_response(data=data)


class RecentDossiersView(DashboardFilterMixin, APIView):
    """Derniers dossiers créés."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Dossiers récents',
        parameters=[COMMUNE_PARAM, LIMIT_PARAM],
        responses={200: RecentDossierSerializer(many=True)},
    )
    def get(self, request):
        data = DashboardStatsService.get_recent_dossiers(
            commune=self.get_commune_filter(),
            limit=self.get_limit_filter(),
        )
        return success_response(data=data)


class StaleDossiersView(DashboardFilterMixin, APIView):
    """Dossiers bloqués depuis plus de N heures."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Dossiers en attente (stale)',
        parameters=[
            COMMUNE_PARAM,
            OpenApiParameter(
                name='hours', type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY, required=False,
                description='Seuil en heures (défaut: 48).',
            ),
        ],
    )
    def get(self, request):
        try:
            hours = int(request.query_params.get('hours', 48))
            hours = min(max(hours, 1), 720)  # Entre 1h et 30 jours
        except (ValueError, TypeError):
            hours = 48

        stale_qs = DashboardStatsService.get_stale_dossiers(
            commune=self.get_commune_filter(),
            stale_hours=hours,
        )
        data = [
            {
                'reference': d.reference,
                'citizen_name': d.citizen.full_name,
                'commune_name': d.commune.name,
                'status': d.status,
                'status_display': d.get_status_display(),
                'submitted_at': d.submitted_at,
                'assigned_agent': d.assigned_agent.full_name if d.assigned_agent else None,
            }
            for d in stale_qs[:50]
        ]
        return success_response(data=data)


# =============================================================================
# EXPORT CSV (FONCTIONNALITÉ PREMIUM)
# =============================================================================

class ExportDossiersCSVView(DashboardFilterMixin, APIView):
    """
    GET /api/dashboard/export-csv/
    Génère et télécharge un fichier CSV de tous les dossiers.
    Inclut un log d'audit pour tracer les exports.
    """
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Exporter les données en CSV',
        parameters=[COMMUNE_PARAM],
    )
    def get(self, request):
        commune = self.get_commune_filter()
        qs = Dossier.objects.select_related(
            'citizen', 'commune', 'assigned_agent',
        ).all()

        if commune:
            qs = qs.filter(commune=commune)

        # Log d'audit de l'export
        logger.info(
            f'[CSV Export] Utilisateur {request.user.email} (role={request.user.role}) '
            f'exporte {qs.count()} dossier(s). '
            f'Commune filtre : {commune.name if commune else "toutes"}.'
        )

        # Horodatage dans le nom de fichier
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'rapport_dossiers_{timestamp}.csv'

        # Création de la réponse HTTP avec le type CSV
        response = HttpResponse(
            content_type='text/csv; charset=utf-8',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )

        # Encodage UTF-8 avec BOM pour une ouverture parfaite dans Excel
        response.write('\ufeff'.encode('utf8'))
        writer = csv.writer(response, delimiter=';')

        # En-têtes
        writer.writerow([
            'Référence', 'Type', 'Statut', 'Citoyen', 'Email Citoyen',
            'Agent Assigné', 'Commune', 'Date de création', 'Date de soumission',
            'Date de finalisation',
        ])

        # Remplissage avec protection contre les données null
        for d in qs.iterator(chunk_size=500):
            writer.writerow([
                d.reference or '',
                d.get_type_display(),
                d.get_status_display(),
                d.citizen.full_name if d.citizen else 'N/A',
                d.citizen.email if d.citizen else 'N/A',
                d.assigned_agent.full_name if d.assigned_agent else 'Non assigné',
                d.commune.name if d.commune else 'N/A',
                d.created_at.strftime('%Y-%m-%d %H:%M') if d.created_at else '',
                d.submitted_at.strftime('%Y-%m-%d %H:%M') if d.submitted_at else '',
                d.completed_at.strftime('%Y-%m-%d %H:%M') if d.completed_at else '',
            ])

        return response
