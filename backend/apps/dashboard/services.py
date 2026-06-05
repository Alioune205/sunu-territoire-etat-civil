"""
Dashboard services — Logique métier avec système de Cache (Ultra-Pro).
"""
import logging
from datetime import timedelta
from django.db.models import Count, Avg, Min, Max, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from apps.dossiers.models import Dossier

logger = logging.getLogger('system')
User = get_user_model()

class DashboardStatsService:
    """
    Service centralisé. Utilise le cache Redis/Memcached (ou cache local)
    pour des performances foudroyantes sur les gros volumes de données.
    """

    @staticmethod
    def get_overview(commune=None):
        cache_key = f"dash_overview_{commune.id if commune else 'global'}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        qs = Dossier.objects.all()
        if commune:
            qs = qs.filter(commune=commune)

        total = qs.count()
        completed = qs.filter(status=Dossier.Status.COMPLETED).count()
        processed = qs.filter(submitted_at__isnull=False, completed_at__isnull=False).annotate(
            processing_time=ExpressionWrapper(F('completed_at') - F('submitted_at'), output_field=DurationField())
        )
        avg_delta = processed.aggregate(avg=Avg('processing_time'))['avg']
        
        data = {
            'total_dossiers': total,
            'total_pending': qs.filter(status=Dossier.Status.SUBMITTED).count(),
            'total_in_review': qs.filter(status=Dossier.Status.IN_REVIEW).count(),
            'total_approved': qs.filter(status=Dossier.Status.APPROVED).count(),
            'total_rejected': qs.filter(status=Dossier.Status.REJECTED).count(),
            'total_completed': completed,
            'total_citizens': User.objects.filter(role='citizen', **({'commune': commune} if commune else {})).count(),
            'total_agents': User.objects.exclude(role='citizen').filter(**({'commune': commune} if commune else {})).count(),
            'avg_processing_hours': round(avg_delta.total_seconds() / 3600, 2) if avg_delta else None,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0.0,
        }
        
        # Cache pour 5 minutes
        cache.set(cache_key, data, 300)
        return data

    @staticmethod
    def get_count_by_status(commune=None):
        qs = Dossier.objects.all()
        if commune: qs = qs.filter(commune=commune)
        status_map = dict(Dossier.Status.choices)
        return [{'status': i['status'], 'status_display': status_map.get(i['status'], i['status']), 'count': i['count']} 
                for i in qs.values('status').annotate(count=Count('id')).order_by('status')]

    @staticmethod
    def get_count_by_type(commune=None):
        qs = Dossier.objects.all()
        if commune: qs = qs.filter(commune=commune)
        type_map = dict(Dossier.Type.choices)
        return [{'type': i['type'], 'type_display': type_map.get(i['type'], i['type']), 'count': i['count']} 
                for i in qs.values('type').annotate(count=Count('id')).order_by('type')]

    @staticmethod
    def get_count_by_commune():
        return list(Dossier.objects.values('commune__name', 'commune__region').annotate(count=Count('id')).order_by('-count'))

    @staticmethod
    def get_daily_volume(commune=None, days=30):
        since = timezone.now() - timedelta(days=days)
        qs = Dossier.objects.filter(created_at__gte=since)
        if commune: qs = qs.filter(commune=commune)
        return list(qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date'))

    @staticmethod
    def get_agent_performance(commune=None):
        agent_qs = User.objects.filter(is_active=True).exclude(role='citizen')
        if commune: agent_qs = agent_qs.filter(commune=commune)
        results = []
        for agent in agent_qs:
            assigned = Dossier.objects.filter(assigned_agent=agent)
            processed = assigned.filter(submitted_at__isnull=False, completed_at__isnull=False).annotate(
                processing_time=ExpressionWrapper(F('completed_at') - F('submitted_at'), output_field=DurationField())
            )
            avg_delta = processed.aggregate(avg=Avg('processing_time'))['avg']
            results.append({
                'agent_id': agent.id, 'agent_name': agent.full_name, 'agent_role': agent.get_role_display(),
                'total_assigned': assigned.count(),
                'total_completed': assigned.filter(status__in=[Dossier.Status.COMPLETED, Dossier.Status.APPROVED]).count(),
                'total_rejected': assigned.filter(status=Dossier.Status.REJECTED).count(),
                'avg_processing_hours': round(avg_delta.total_seconds() / 3600, 2) if avg_delta else None,
            })
        return sorted(results, key=lambda x: x['total_completed'], reverse=True)

    @staticmethod
    def get_processing_delays(commune=None):
        qs = Dossier.objects.filter(submitted_at__isnull=False, completed_at__isnull=False)
        if commune: qs = qs.filter(commune=commune)
        qs = qs.annotate(processing_time=ExpressionWrapper(F('completed_at') - F('submitted_at'), output_field=DurationField()))
        type_map = dict(Dossier.Type.choices)
        data = qs.values('type').annotate(avg_time=Avg('processing_time'), min_time=Min('processing_time'), max_time=Max('processing_time'), total_processed=Count('id'))
        return [{'type': i['type'], 'type_display': type_map.get(i['type'], i['type']), 
                 'avg_hours': round(i['avg_time'].total_seconds()/3600, 2) if i['avg_time'] else None,
                 'min_hours': round(i['min_time'].total_seconds()/3600, 2) if i['min_time'] else None,
                 'max_hours': round(i['max_time'].total_seconds()/3600, 2) if i['max_time'] else None,
                 'total_processed': i['total_processed']} for i in data]

    @staticmethod
    def get_recent_dossiers(commune=None, limit=10):
        qs = Dossier.objects.select_related('citizen', 'commune').order_by('-created_at')
        if commune: qs = qs.filter(commune=commune)
        return [{'id': d.id, 'reference': d.reference, 'type': d.type, 'type_display': d.get_type_display(), 'status': d.status, 'status_display': d.get_status_display(), 'citizen_name': d.citizen.full_name, 'commune_name': d.commune.name, 'created_at': d.created_at, 'submitted_at': d.submitted_at} for d in qs[:limit]]

    @staticmethod
    def get_stale_dossiers(commune=None, stale_hours=48):
        threshold = timezone.now() - timedelta(hours=stale_hours)
        qs = Dossier.objects.filter(status__in=[Dossier.Status.SUBMITTED, Dossier.Status.IN_REVIEW], submitted_at__lte=threshold).select_related('citizen', 'commune', 'assigned_agent')
        if commune: qs = qs.filter(commune=commune)
        return qs
