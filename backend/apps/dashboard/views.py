"""
Dashboard statistics views for SUNU CIVIL.
"""
from collections import Counter
from datetime import timedelta

from django.db.models import (
    Count, Q, F, Avg, FloatField, ExpressionWrapper
)
from django.db.models.functions import (
    TruncDay, TruncWeek, TruncMonth
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from apps.shared.permissions import IsAdminStaff
from apps.shared.responses import success_response
from apps.dossiers.models import Dossier
from apps.documents.models import Document


def format_duration(duration):
    """Format a timedelta into a human-readable duration string."""
    if duration is None:
        return '0s'
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f'{hours}h {minutes}m'
    if minutes:
        return f'{minutes}m {seconds}s'
    return f'{seconds}s'


class DashboardStatsView(APIView):
    """API view for dashboard statistics."""

    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Statistiques principales du dashboard'
    )
    def get(self, request):
        """Return global KPIs for the admin dashboard."""
        total_dossiers = Dossier.objects.count()
        total_documents = Document.objects.count()

        status_counts = {
            item['status']: item['count']
            for item in Dossier.objects.values(
                'status'
            ).annotate(count=Count('id'))
        }

        commune_counts = [
            {
                'commune': item['commune__name'] or 'Inconnue',
                'count': item['count'],
            }
            for item in Dossier.objects.values(
                'commune__name'
            ).annotate(
                count=Count('id')
            ).order_by('-count')
        ]

        document_type_counts = {
            item['file_type']: item['count']
            for item in Document.objects.values(
                'file_type'
            ).annotate(count=Count('id'))
        }

        review_durations = []
        completion_durations = []

        for dossier in Dossier.objects.exclude(
            submitted_at__isnull=True
        ).exclude(
            reviewed_at__isnull=True
        ).values('submitted_at', 'reviewed_at'):
            review_durations.append(
                dossier['reviewed_at'] - dossier['submitted_at']
            )

        for dossier in Dossier.objects.exclude(
            submitted_at__isnull=True
        ).exclude(
            completed_at__isnull=True
        ).values('submitted_at', 'completed_at'):
            completion_durations.append(
                dossier['completed_at'] - dossier['submitted_at']
            )

        average_review_time = (
            sum(
                (d.total_seconds() for d in review_durations), 0
            ) / len(review_durations)
            if review_durations else 0
        )
        average_completion_time = (
            sum(
                (d.total_seconds() for d in completion_durations), 0
            ) / len(completion_durations)
            if completion_durations else 0
        )

        data = {
            'total_dossiers': total_dossiers,
            'total_documents': total_documents,
            'status_counts': status_counts,
            'dossiers_by_commune': commune_counts,
            'documents_by_type': document_type_counts,
            'average_review_time': format_duration(
                timedelta(seconds=average_review_time)
            ),
            'average_completion_time': format_duration(
                timedelta(seconds=average_completion_time)
            ),
        }

        return success_response(data=data)


class GlobalStatsView(APIView):
    """API for global statistics."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Statistiques globales'
    )
    def get(self, request):
        stats = Dossier.objects.aggregate(
            total=Count('id'),
            en_cours=Count(
                'id',
                filter=Q(status__in=[
                    Dossier.Status.SUBMITTED,
                    Dossier.Status.IN_REVIEW
                ])
            ),
            valides=Count(
                'id',
                filter=Q(status=Dossier.Status.APPROVED)
            ),
            rejetes=Count(
                'id',
                filter=Q(status=Dossier.Status.REJECTED)
            )
        )
        total = stats['total']
        taux = (
            round((stats['valides'] / total * 100), 2)
            if total and total > 0 else 0.0
        )

        return success_response({
            "total_dossiers": total,
            "dossiers_en_cours": stats['en_cours'],
            "dossiers_valides": stats['valides'],
            "dossiers_rejetes": stats['rejetes'],
            "taux_approbation": taux
        })


class PerformanceStatsView(APIView):
    """API for performance statistics."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary='Statistiques de performance'
    )
    def get(self, request):
        time_diff = ExpressionWrapper(
            F('completed_at') - F('submitted_at'),
            output_field=FloatField()
        )
        avg_time_query = Dossier.objects.filter(
            status__in=[
                Dossier.Status.APPROVED,
            ],
            submitted_at__isnull=False,
            completed_at__isnull=False
        ).aggregate(temps_moyen=Avg(time_diff))

        perf_communes = Dossier.objects.values(
            'commune__name'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:10]

        perf_agents = Dossier.objects.filter(
            assigned_agent__isnull=False
        ).values(
            'assigned_agent__email'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:10]

        return success_response({
            "temps_moyen_traitement_secondes": (
                avg_time_query['temps_moyen'] or 0
            ),
            "performance_communes": list(perf_communes),
            "performance_agents": list(perf_agents)
        })


class ActivityStatsView(APIView):
    """API for activity statistics."""
    permission_classes = [IsAuthenticated, IsAdminStaff]

    @extend_schema(
        tags=['Dashboard'],
        summary="Statistiques d'activité"
    )
    def get(self, request):
        daily = Dossier.objects.annotate(
            date=TruncDay('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('-date')[:7]

        weekly = Dossier.objects.annotate(
            date=TruncWeek('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('-date')[:4]

        monthly = Dossier.objects.annotate(
            date=TruncMonth('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('-date')[:12]

        return success_response({
            "daily": list(daily),
            "weekly": list(weekly),
            "monthly": list(monthly)
        })
