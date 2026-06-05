"""
Dashboard services — Logique métier pour les statistiques et rapports.
Centralise les requêtes d'agrégation pour éviter de surcharger les vues.
"""
import logging
from datetime import timedelta

from django.db.models import Count, Avg, Min, Max, F, Q, ExpressionWrapper, DurationField
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.dossiers.models import Dossier

logger = logging.getLogger('system')
User = get_user_model()


class DashboardStatsService:
    """
    Service centralisé pour les requêtes statistiques du dashboard.
    Toutes les méthodes sont statiques et pures (pas d'effets de bord).
    """

    @staticmethod
    def get_overview(commune=None):
        """
        Statistiques globales : totaux par statut, taux de complétion, délai moyen.
        Si commune est fourni, filtre les résultats.
        """
        qs = Dossier.objects.all()
        if commune:
            qs = qs.filter(commune=commune)

        total = qs.count()
        pending = qs.filter(status=Dossier.Status.SUBMITTED).count()
        in_review = qs.filter(status=Dossier.Status.IN_REVIEW).count()
        approved = qs.filter(status=Dossier.Status.APPROVED).count()
        rejected = qs.filter(status=Dossier.Status.REJECTED).count()
        completed = qs.filter(status=Dossier.Status.COMPLETED).count()

        # Délai moyen de traitement (soumission → complétion)
        processed = qs.filter(
            submitted_at__isnull=False,
            completed_at__isnull=False,
        ).annotate(
            processing_time=ExpressionWrapper(
                F('completed_at') - F('submitted_at'),
                output_field=DurationField()
            )
        )
        avg_delta = processed.aggregate(avg=Avg('processing_time'))['avg']
        avg_hours = avg_delta.total_seconds() / 3600 if avg_delta else None

        # Nombre de citoyens et agents
        user_qs = User.objects.filter(is_active=True)
        if commune:
            user_qs = user_qs.filter(commune=commune)
        total_citizens = user_qs.filter(role='citizen').count()
        total_agents = user_qs.exclude(role='citizen').count()

        completion_rate = round((completed / total) * 100, 2) if total > 0 else 0.0

        return {
            'total_dossiers': total,
            'total_pending': pending,
            'total_in_review': in_review,
            'total_approved': approved,
            'total_rejected': rejected,
            'total_completed': completed,
            'total_citizens': total_citizens,
            'total_agents': total_agents,
            'avg_processing_hours': round(avg_hours, 2) if avg_hours else None,
            'completion_rate': completion_rate,
        }

    @staticmethod
    def get_count_by_status(commune=None):
        """Répartition des dossiers par statut."""
        qs = Dossier.objects.all()
        if commune:
            qs = qs.filter(commune=commune)

        status_map = dict(Dossier.Status.choices)
        data = qs.values('status').annotate(count=Count('id')).order_by('status')
        return [
            {
                'status': item['status'],
                'status_display': status_map.get(item['status'], item['status']),
                'count': item['count'],
            }
            for item in data
        ]

    @staticmethod
    def get_count_by_type(commune=None):
        """Répartition des dossiers par type."""
        qs = Dossier.objects.all()
        if commune:
            qs = qs.filter(commune=commune)

        type_map = dict(Dossier.Type.choices)
        data = qs.values('type').annotate(count=Count('id')).order_by('type')
        return [
            {
                'type': item['type'],
                'type_display': type_map.get(item['type'], item['type']),
                'count': item['count'],
            }
            for item in data
        ]

    @staticmethod
    def get_count_by_commune():
        """Répartition des dossiers par commune (admin global)."""
        data = (
            Dossier.objects
            .values('commune__name', 'commune__region')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return list(data)

    @staticmethod
    def get_daily_volume(commune=None, days=30):
        """Volume quotidien de dossiers créés sur les N derniers jours."""
        since = timezone.now() - timedelta(days=days)
        qs = Dossier.objects.filter(created_at__gte=since)
        if commune:
            qs = qs.filter(commune=commune)

        data = (
            qs.annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        return list(data)

    @staticmethod
    def get_agent_performance(commune=None):
        """Performance individuelle des agents."""
        agent_qs = User.objects.filter(is_active=True).exclude(role='citizen')
        if commune:
            agent_qs = agent_qs.filter(commune=commune)

        results = []
        for agent in agent_qs:
            assigned = Dossier.objects.filter(assigned_agent=agent)
            total_assigned = assigned.count()
            total_completed = assigned.filter(
                status__in=[Dossier.Status.COMPLETED, Dossier.Status.APPROVED]
            ).count()
            total_rejected = assigned.filter(status=Dossier.Status.REJECTED).count()

            # Délai moyen de traitement
            processed = assigned.filter(
                submitted_at__isnull=False,
                completed_at__isnull=False,
            ).annotate(
                processing_time=ExpressionWrapper(
                    F('completed_at') - F('submitted_at'),
                    output_field=DurationField()
                )
            )
            avg_delta = processed.aggregate(avg=Avg('processing_time'))['avg']
            avg_hours = round(avg_delta.total_seconds() / 3600, 2) if avg_delta else None

            results.append({
                'agent_id': agent.id,
                'agent_name': agent.full_name,
                'agent_role': agent.get_role_display(),
                'total_assigned': total_assigned,
                'total_completed': total_completed,
                'total_rejected': total_rejected,
                'avg_processing_hours': avg_hours,
            })

        return sorted(results, key=lambda x: x['total_completed'], reverse=True)

    @staticmethod
    def get_processing_delays(commune=None):
        """Délais de traitement par type de dossier."""
        qs = Dossier.objects.filter(
            submitted_at__isnull=False,
            completed_at__isnull=False,
        )
        if commune:
            qs = qs.filter(commune=commune)

        qs = qs.annotate(
            processing_time=ExpressionWrapper(
                F('completed_at') - F('submitted_at'),
                output_field=DurationField()
            )
        )

        type_map = dict(Dossier.Type.choices)
        data = (
            qs.values('type')
            .annotate(
                avg_time=Avg('processing_time'),
                min_time=Min('processing_time'),
                max_time=Max('processing_time'),
                total_processed=Count('id'),
            )
            .order_by('type')
        )

        results = []
        for item in data:
            results.append({
                'type': item['type'],
                'type_display': type_map.get(item['type'], item['type']),
                'avg_hours': round(item['avg_time'].total_seconds() / 3600, 2) if item['avg_time'] else None,
                'min_hours': round(item['min_time'].total_seconds() / 3600, 2) if item['min_time'] else None,
                'max_hours': round(item['max_time'].total_seconds() / 3600, 2) if item['max_time'] else None,
                'total_processed': item['total_processed'],
            })
        return results

    @staticmethod
    def get_recent_dossiers(commune=None, limit=10):
        """Derniers dossiers soumis."""
        qs = Dossier.objects.select_related('citizen', 'commune').order_by('-created_at')
        if commune:
            qs = qs.filter(commune=commune)

        results = []
        for d in qs[:limit]:
            results.append({
                'id': d.id,
                'reference': d.reference,
                'type': d.type,
                'type_display': d.get_type_display(),
                'status': d.status,
                'status_display': d.get_status_display(),
                'citizen_name': d.citizen.full_name,
                'commune_name': d.commune.name,
                'created_at': d.created_at,
                'submitted_at': d.submitted_at,
            })
        return results

    @staticmethod
    def get_stale_dossiers(commune=None, stale_hours=48):
        """
        Dossiers en attente depuis plus de N heures (alerte urgence).
        Utilisé pour les notifications d'alerte agents.
        """
        threshold = timezone.now() - timedelta(hours=stale_hours)
        qs = Dossier.objects.filter(
            status__in=[Dossier.Status.SUBMITTED, Dossier.Status.IN_REVIEW],
            submitted_at__lte=threshold,
        ).select_related('citizen', 'commune', 'assigned_agent')

        if commune:
            qs = qs.filter(commune=commune)

        return qs
