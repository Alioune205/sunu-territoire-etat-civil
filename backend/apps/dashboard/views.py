"""
Dashboard views — 5 endpoints analytiques pour le dashboard React.
DEV 2A: Pape Alioune Sène

Chemin : backend/apps/dashboard/views.py
Rôle   : Expose les données statistiques via des APIViews simples.
         Toute la logique métier est déléguée aux services.
Impact : Aucun conflit avec les views existantes. Utilise les permissions
         déjà définies dans apps.shared.permissions.

Endpoints implémentés :
  GET /api/dashboard/stats/          → DashboardStatsView
  GET /api/dashboard/kpis/           → DashboardKPIsView
  GET /api/dashboard/charts/         → DashboardChartsView
  GET /api/dashboard/activity/       → DashboardActivityView
  GET /api/dashboard/recent-actions/ → DashboardRecentActionsView
  GET /api/dashboard/search/         → DashboardSearchView

Permissions :
  - IsAdminStaff : agents, civil_admin, super_admin uniquement
  - Les citoyens n'ont pas accès au dashboard
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.shared.permissions import IsAdminStaff
from apps.shared.responses import success_response, error_response

from .services import (
    get_dashboard_stats,
    get_dashboard_kpis,
    get_dashboard_charts,
    get_recent_activity,
)
from .serializers import (
    DashboardStatsSerializer,
    DashboardKPIsSerializer,
    DashboardChartsSerializer,
    RecentActivitySerializer,
)
from .filters import DossierDashboardFilter, AuditLogDashboardFilter

from apps.audit_logs.models import AuditLog
from apps.dossiers.models import Dossier


# ---------------------------------------------------------------------------
# 1. Stats globales
# ---------------------------------------------------------------------------

@extend_schema(
    tags=['Dashboard'],
    summary='Statistiques globales du système',
    description=(
        'Retourne le nombre total de dossiers, la répartition par statut '
        'et par type d\'acte, ainsi que les totaux utilisateurs et communes. '
        'Les données sont filtrées selon la commune de l\'utilisateur '
        '(sauf super_admin qui voit tout).'
    ),
    responses={200: DashboardStatsSerializer},
)
class DashboardStatsView(APIView):
    """GET /api/dashboard/stats/"""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    def get(self, request):
        data = get_dashboard_stats(request.user)
        serializer = DashboardStatsSerializer(data)
        return success_response(
            data=serializer.data,
            message='Statistiques globales récupérées avec succès.',
        )


# ---------------------------------------------------------------------------
# 2. KPIs
# ---------------------------------------------------------------------------

@extend_schema(
    tags=['Dashboard'],
    summary='KPIs de performance',
    description=(
        'Calcule les indicateurs clés : temps moyen de traitement par commune '
        '(de la soumission à la complétion), taux de rejet global et par commune, '
        'et productivité de chaque agent (dossiers traités, approuvés, rejetés).'
    ),
    responses={200: DashboardKPIsSerializer},
)
class DashboardKPIsView(APIView):
    """GET /api/dashboard/kpis/"""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    def get(self, request):
        data = get_dashboard_kpis(request.user)
        serializer = DashboardKPIsSerializer(data)
        return success_response(
            data=serializer.data,
            message='KPIs récupérés avec succès.',
        )


# ---------------------------------------------------------------------------
# 3. Charts
# ---------------------------------------------------------------------------

@extend_schema(
    tags=['Dashboard'],
    summary='Données pour graphiques de tendances',
    description=(
        'Retourne les volumes journaliers et hebdomadaires de dépôts de dossiers '
        'ainsi que le profil d\'activité horaire (à quelle heure les dossiers sont '
        'soumis). Utilisé pour alimenter les graphiques Recharts du frontend React.'
    ),
    parameters=[
        OpenApiParameter(
            name='days',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Fenêtre temporelle en jours (défaut: 30, min: 7, max: 365)',
            required=False,
        ),
    ],
    responses={200: DashboardChartsSerializer},
)
class DashboardChartsView(APIView):
    """GET /api/dashboard/charts/?days=30"""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    def get(self, request):
        try:
            days = int(request.query_params.get('days', 30))
        except (ValueError, TypeError):
            days = 30

        data = get_dashboard_charts(request.user, days=days)
        serializer = DashboardChartsSerializer(data)
        return success_response(
            data=serializer.data,
            message='Données graphiques récupérées avec succès.',
        )


# ---------------------------------------------------------------------------
# 4. Activity feed
# ---------------------------------------------------------------------------

@extend_schema(
    tags=['Dashboard'],
    summary='Flux d\'activité récente (Audit Logs)',
    description=(
        'Retourne les N derniers logs d\'activité système : connexions, '
        'modifications, changements de statut, uploads. '
        'Basé sur le modèle AuditLog. Super admin voit tout, '
        'les autres voient les actions de leur commune.'
    ),
    parameters=[
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Nombre de logs à retourner (défaut: 20, max: 100)',
            required=False,
        ),
        OpenApiParameter(
            name='action',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filtrer par type d\'action (LOGIN, CREATE, STATUS_CHANGE...)',
            required=False,
        ),
        OpenApiParameter(
            name='date_from',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Date de début (YYYY-MM-DD)',
            required=False,
        ),
        OpenApiParameter(
            name='date_to',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Date de fin (YYYY-MM-DD)',
            required=False,
        ),
    ],
    responses={200: RecentActivitySerializer(many=True)},
)
class DashboardActivityView(APIView):
    """GET /api/dashboard/activity/"""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 20))
        except (ValueError, TypeError):
            limit = 20

        # Appliquer les filtres django-filter sur AuditLog
        audit_qs = AuditLog.objects.select_related('user', 'user__commune')
        if request.user.role != 'super_admin' and request.user.commune_id:
            from django.db.models import Q
            audit_qs = audit_qs.filter(
                Q(user__commune=request.user.commune) | Q(user=request.user)
            )

        filterset = AuditLogDashboardFilter(request.query_params, queryset=audit_qs)
        if filterset.is_valid():
            audit_qs = filterset.qs

        audit_qs = audit_qs.order_by('-created_at')[:limit]

        action_display_map = dict(AuditLog.Action.choices)
        result = []
        for log in audit_qs:
            result.append({
                'id': log.id,
                'user_name': log.user.full_name if log.user else None,
                'user_email': log.user.email if log.user else None,
                'user_role': log.user.role if log.user else None,
                'action': log.action,
                'action_display': action_display_map.get(log.action, log.action),
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'details': log.details,
                'ip_address': str(log.ip_address) if log.ip_address else None,
                'created_at': log.created_at,
            })

        serializer = RecentActivitySerializer(result, many=True)
        return success_response(
            data=serializer.data,
            message=f'{len(result)} action(s) récente(s) récupérée(s).',
        )


# ---------------------------------------------------------------------------
# 5. Recent Actions (alias enrichi de Activity)
# ---------------------------------------------------------------------------

@extend_schema(
    tags=['Dashboard'],
    summary='Dernières actions importantes',
    description=(
        'Retourne les 10 dernières actions sensibles (connexions, changements '
        'de statut, modifications de rôles). Endpoint optimisé pour le widget '
        '"Activité récente" du dashboard React.'
    ),
    responses={200: RecentActivitySerializer(many=True)},
)
class DashboardRecentActionsView(APIView):
    """GET /api/dashboard/recent-actions/"""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    # Actions considérées comme "importantes" pour ce widget
    IMPORTANT_ACTIONS = [
        AuditLog.Action.LOGIN,
        AuditLog.Action.STATUS_CHANGE,
        AuditLog.Action.ROLE_CHANGE,
        AuditLog.Action.DELETE,
    ]

    def get(self, request):
        data = get_recent_activity(request.user, limit=10)
        # Filtrer sur les actions importantes uniquement
        filtered = [
            item for item in data
            if item['action'] in self.IMPORTANT_ACTIONS
        ]
        serializer = RecentActivitySerializer(filtered, many=True)
        return success_response(
            data=serializer.data,
            message='Dernières actions importantes récupérées.',
        )


# ---------------------------------------------------------------------------
# 6. Recherche avancée sur les dossiers (bonus implémenté)
# ---------------------------------------------------------------------------

@extend_schema(
    tags=['Dashboard'],
    summary='Recherche et filtrage avancés des dossiers',
    description=(
        'Endpoint de recherche puissant pour le dashboard. '
        'Supporte : ?commune=<uuid>, ?status=submitted, ?type=birth_certificate, '
        '?assigned_agent=<uuid>, ?date_from=2026-01-01, ?date_to=2026-06-30, '
        '?search=<texte> (recherche sur référence, nom citoyen, numéro CNI). '
        'Résultats paginés (page_size=20 par défaut).'
    ),
    parameters=[
        OpenApiParameter('commune', OpenApiTypes.UUID, OpenApiParameter.QUERY),
        OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter('type', OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter('assigned_agent', OpenApiTypes.UUID, OpenApiParameter.QUERY),
        OpenApiParameter('date_from', OpenApiTypes.DATE, OpenApiParameter.QUERY),
        OpenApiParameter('date_to', OpenApiTypes.DATE, OpenApiParameter.QUERY),
        OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter('page', OpenApiTypes.INT, OpenApiParameter.QUERY),
        OpenApiParameter('page_size', OpenApiTypes.INT, OpenApiParameter.QUERY),
    ],
)
class DashboardSearchView(APIView):
    """GET /api/dashboard/search/"""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    def get(self, request):
        from apps.shared.pagination import StandardPagination
        from apps.dossiers.serializers import DossierListSerializer

        # Scope de base selon le rôle
        if request.user.role == 'super_admin':
            qs = Dossier.objects.all()
        elif request.user.commune_id:
            qs = Dossier.objects.filter(commune=request.user.commune)
        else:
            return success_response(data=[], message='Aucun dossier accessible.')

        qs = qs.select_related('citizen', 'assigned_agent', 'commune')

        # Appliquer les filtres avancés
        filterset = DossierDashboardFilter(request.query_params, queryset=qs)
        if not filterset.is_valid():
            return error_response(
                errors=filterset.errors,
                message='Paramètres de filtrage invalides.',
            )
        qs = filterset.qs.order_by('-created_at')

        # Paginer
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        if page is not None:
            serializer = DossierListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = DossierListSerializer(qs, many=True)
        return success_response(data=serializer.data)
