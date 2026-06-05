"""
Dashboard views — API endpoints pour les statistiques et rapports.
Inclut l'Export CSV et la mise en cache (Ultra-Pro).
"""
import csv
from django.http import HttpResponse
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

# Paramètres Swagger
COMMUNE_PARAM = OpenApiParameter(name='commune', type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY, required=False)
DAYS_PARAM = OpenApiParameter(name='days', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False)
LIMIT_PARAM = OpenApiParameter(name='limit', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False)


class OverviewView(DashboardFilterMixin, APIView):
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(tags=['Dashboard'], summary='Vue d\'ensemble avec Cache', responses={200: OverviewStatsSerializer})
    def get(self, request):
        commune = self.get_commune_filter()
        data = DashboardStatsService.get_overview(commune=commune)
        return success_response(data=data)


class CountByStatusView(DashboardFilterMixin, APIView):
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(tags=['Dashboard'], responses={200: DossierCountByStatusSerializer(many=True)})
    def get(self, request):
        data = DashboardStatsService.get_count_by_status(commune=self.get_commune_filter())
        return success_response(data=data)


class CountByTypeView(DashboardFilterMixin, APIView):
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(tags=['Dashboard'], responses={200: DossierCountByTypeSerializer(many=True)})
    def get(self, request):
        data = DashboardStatsService.get_count_by_type(commune=self.get_commune_filter())
        return success_response(data=data)


class CountByCommuneView(APIView):
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(tags=['Dashboard'], responses={200: DossierCountByCommuneSerializer(many=True)})
    def get(self, request):
        if request.user.role != 'super_admin':
            return error_response(message='Réservé au super administrateur.', status_code=403)
        return success_response(data=DashboardStatsService.get_count_by_commune())


class DailyVolumeView(DashboardFilterMixin, APIView):
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(tags=['Dashboard'], parameters=[DAYS_PARAM], responses={200: DailyVolumeSerializer(many=True)})
    def get(self, request):
        data = DashboardStatsService.get_daily_volume(commune=self.get_commune_filter(), days=self.get_days_filter())
        return success_response(data=data)


class AgentPerformanceView(DashboardFilterMixin, APIView):
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(tags=['Dashboard'], responses={200: AgentPerformanceSerializer(many=True)})
    def get(self, request):
        data = DashboardStatsService.get_agent_performance(commune=self.get_commune_filter())
        return success_response(data=data)


class ProcessingDelaysView(DashboardFilterMixin, APIView):
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(tags=['Dashboard'], responses={200: ProcessingDelaySerializer(many=True)})
    def get(self, request):
        data = DashboardStatsService.get_processing_delays(commune=self.get_commune_filter())
        return success_response(data=data)


class RecentDossiersView(DashboardFilterMixin, APIView):
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(tags=['Dashboard'], parameters=[LIMIT_PARAM], responses={200: RecentDossierSerializer(many=True)})
    def get(self, request):
        data = DashboardStatsService.get_recent_dossiers(commune=self.get_commune_filter(), limit=self.get_limit_filter())
        return success_response(data=data)


class StaleDossiersView(DashboardFilterMixin, APIView):
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(tags=['Dashboard'])
    def get(self, request):
        try:
            hours = int(request.query_params.get('hours', 48))
        except ValueError:
            hours = 48
        stale_qs = DashboardStatsService.get_stale_dossiers(commune=self.get_commune_filter(), stale_hours=hours)
        data = [{'reference': d.reference, 'citizen_name': d.citizen.full_name, 'status': d.status} for d in stale_qs[:50]]
        return success_response(data=data)


# =============================================================================
# EXPORT CSV (FONCTIONNALITÉ PREMIUM DEV 2B)
# =============================================================================

class ExportDossiersCSVView(DashboardFilterMixin, APIView):
    """
    GET /api/dashboard/export-csv/
    Génère et télécharge un fichier CSV de tous les dossiers (pour le Maire ou l'Admin).
    Montre une maîtrise avancée du backend (Génération de fichiers à la volée).
    """
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(tags=['Dashboard'], summary="Exporter les données en CSV")
    def get(self, request):
        commune = self.get_commune_filter()
        qs = Dossier.objects.select_related('citizen', 'commune', 'assigned_agent').all()
        if commune:
            qs = qs.filter(commune=commune)

        # Création de la réponse HTTP avec le type CSV
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="rapport_dossiers.csv"'},
        )
        
        # Encodage UTF-8 avec BOM pour une ouverture parfaite dans Excel
        response.write('\ufeff'.encode('utf8'))
        writer = csv.writer(response, delimiter=';')

        # En-têtes
        writer.writerow(['Référence', 'Type', 'Statut', 'Citoyen', 'Email Citoyen', 'Agent Assigné', 'Commune', 'Date de création'])

        # Remplissage
        for d in qs:
            writer.writerow([
                d.reference,
                d.get_type_display(),
                d.get_status_display(),
                d.citizen.full_name,
                d.citizen.email,
                d.assigned_agent.full_name if d.assigned_agent else "Non assigné",
                d.commune.name,
                d.created_at.strftime("%Y-%m-%d %H:%M")
            ])

        return response
