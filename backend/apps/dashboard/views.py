"""
Dashboard views.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema

from apps.dossiers.models import Dossier

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Dashboard'], summary='Statistiques globales')
    def get(self, request, *args, **kwargs):
        # 1. Global statistics & Rates
        total_dossiers = Dossier.objects.count()
        status_counts = Dossier.objects.values('status').annotate(count=Count('id'))
        
        status_stats = {item['status']: item['count'] for item in status_counts}

        approved_count = status_stats.get(Dossier.Status.APPROVED, 0) + status_stats.get(Dossier.Status.COMPLETED, 0)
        rejected_count = status_stats.get(Dossier.Status.REJECTED, 0)
        approval_rate = round((approved_count / total_dossiers * 100), 2) if total_dossiers > 0 else 0
        rejection_rate = round((rejected_count / total_dossiers * 100), 2) if total_dossiers > 0 else 0

        # 2. Performance: average processing time (completed_at - submitted_at)
        completed_dossiers = Dossier.objects.filter(
            status=Dossier.Status.COMPLETED,
            submitted_at__isnull=False,
            completed_at__isnull=False
        )
        
        # Global Avg
        global_avg = completed_dossiers.aggregate(
            avg_time=Avg(F('completed_at') - F('submitted_at'))
        )['avg_time']
        avg_time_days = global_avg.days if global_avg else 0

        # Avg by Commune
        commune_perf = completed_dossiers.values('commune__name').annotate(
            avg_time=Avg(F('completed_at') - F('submitted_at'))
        )
        commune_stats = [
            {'commune': item['commune__name'], 'avg_days': item['avg_time'].days if item['avg_time'] else 0}
            for item in commune_perf
        ]

        # Avg by Agent
        agent_perf = completed_dossiers.filter(assigned_agent__isnull=False).values(
            'assigned_agent__first_name', 'assigned_agent__last_name'
        ).annotate(
            avg_time=Avg(F('completed_at') - F('submitted_at'))
        )
        agent_stats = [
            {'agent': f"{item['assigned_agent__first_name']} {item['assigned_agent__last_name']}", 'avg_days': item['avg_time'].days if item['avg_time'] else 0}
            for item in agent_perf
        ]

        # 3. Daily volumes for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_dossiers = Dossier.objects.filter(created_at__gte=thirty_days_ago)
        
        daily_volumes = recent_dossiers.annotate(date=TruncDate('created_at')) \
            .values('date') \
            .annotate(count=Count('id')) \
            .order_by('date')

        daily_stats = [{'date': item['date'].strftime('%Y-%m-%d'), 'count': item['count']} for item in daily_volumes]

        data = {
            'total_dossiers': total_dossiers,
            'approval_rate_percent': approval_rate,
            'rejection_rate_percent': rejection_rate,
            'status_breakdown': status_stats,
            'average_processing_time_days': avg_time_days,
            'performance_by_commune': commune_stats,
            'performance_by_agent': agent_stats,
            'daily_activity': daily_stats
        }

        return Response(data)
