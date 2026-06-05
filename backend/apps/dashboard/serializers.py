"""
Dashboard serializers — structured response schemas for all analytics endpoints.
DEV 2A: Pape Alioune Sène

Chemin : backend/apps/dashboard/serializers.py
Rôle   : Définit la forme exacte de chaque réponse JSON du dashboard.
Impact : Aucun effet sur les modèles existants. Read-only uniquement.
"""
from rest_framework import serializers


# ---------------------------------------------------------------------------
# /api/dashboard/stats/
# ---------------------------------------------------------------------------

class DossierStatusCountSerializer(serializers.Serializer):
    """Répartition des dossiers par statut."""
    status = serializers.CharField()
    status_display = serializers.CharField()
    count = serializers.IntegerField()


class DossierTypeCountSerializer(serializers.Serializer):
    """Répartition des dossiers par type d'acte."""
    type = serializers.CharField()
    type_display = serializers.CharField()
    count = serializers.IntegerField()


class DashboardStatsSerializer(serializers.Serializer):
    """Statistiques globales — /api/dashboard/stats/"""
    total_dossiers = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_communes = serializers.IntegerField()
    by_status = DossierStatusCountSerializer(many=True)
    by_type = DossierTypeCountSerializer(many=True)


# ---------------------------------------------------------------------------
# /api/dashboard/kpis/
# ---------------------------------------------------------------------------

class CommuneProcessingKPISerializer(serializers.Serializer):
    """KPI de traitement par commune."""
    commune_id = serializers.UUIDField()
    commune_name = serializers.CharField()
    avg_processing_hours = serializers.FloatField(allow_null=True)
    total_dossiers = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    rejected_count = serializers.IntegerField()
    rejection_rate_percent = serializers.FloatField()


class AgentProductivitySerializer(serializers.Serializer):
    """Productivité par agent."""
    agent_id = serializers.UUIDField()
    agent_name = serializers.CharField()
    commune_name = serializers.CharField(allow_null=True)
    dossiers_handled = serializers.IntegerField()
    approved = serializers.IntegerField()
    rejected = serializers.IntegerField()
    avg_processing_hours = serializers.FloatField(allow_null=True)


class DashboardKPIsSerializer(serializers.Serializer):
    """KPIs — /api/dashboard/kpis/"""
    global_rejection_rate_percent = serializers.FloatField()
    global_avg_processing_hours = serializers.FloatField(allow_null=True)
    pending_over_48h = serializers.IntegerField(help_text="Dossiers en attente depuis plus de 48h")
    by_commune = CommuneProcessingKPISerializer(many=True)
    agent_productivity = AgentProductivitySerializer(many=True)


# ---------------------------------------------------------------------------
# /api/dashboard/charts/
# ---------------------------------------------------------------------------

class DailyVolumeSerializer(serializers.Serializer):
    """Volume de dépôts par jour."""
    date = serializers.DateField()
    count = serializers.IntegerField()


class HourlyActivitySerializer(serializers.Serializer):
    """Activité par heure de la journée."""
    hour = serializers.IntegerField()
    count = serializers.IntegerField()


class WeeklyVolumeSerializer(serializers.Serializer):
    """Volume de dépôts par semaine."""
    week = serializers.CharField()   # ex: "2026-W22"
    count = serializers.IntegerField()


class DashboardChartsSerializer(serializers.Serializer):
    """Données graphiques — /api/dashboard/charts/"""
    daily_volume = DailyVolumeSerializer(many=True)
    weekly_volume = WeeklyVolumeSerializer(many=True)
    hourly_activity = HourlyActivitySerializer(many=True)


# ---------------------------------------------------------------------------
# /api/dashboard/activity/  &  /api/dashboard/recent-actions/
# ---------------------------------------------------------------------------

class RecentActivitySerializer(serializers.Serializer):
    """Entrée de log d'activité récente."""
    id = serializers.UUIDField()
    user_name = serializers.CharField(allow_null=True)
    user_email = serializers.CharField(allow_null=True)
    user_role = serializers.CharField(allow_null=True)
    action = serializers.CharField()
    action_display = serializers.CharField()
    resource_type = serializers.CharField()
    resource_id = serializers.UUIDField(allow_null=True)
    details = serializers.DictField()
    ip_address = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
