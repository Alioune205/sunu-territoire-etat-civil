from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from apps.shared.responses import error_response
from .models import PaymentTransaction
from .serializers import PaymentTransactionSerializer
from drf_spectacular.utils import extend_schema

class IsSuperAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and hasattr(request.user, 'role') and request.user.role == 'super_admin'

class AdminTransactionListView(ListAPIView):
    """
    GET /api/v1/admin/transactions
    Permet au super administrateur de lister les transactions de paiement avec filtres et pagination.
    """
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        queryset = PaymentTransaction.objects.all().prefetch_related('treasury_transfers')

        # Filtre par type de paiement
        payment_type = self.request.query_params.get('payment_type')
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)

        # Filtre par statut
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filtre par date de début (YYYY-MM-DD)
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        # Filtre par date de fin (YYYY-MM-DD)
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset

    @extend_schema(
        tags=['Paiements'],
        summary='Liste des transactions de paiement',
        description='Récupère les transactions de paiement filtrées pour le rôle Super Admin.'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

from rest_framework.views import APIView
from django.db.models import Sum, Count
from django.utils import timezone
from apps.shared.responses import success_response
from .models import PaymentStatus

class AdminTransactionStatsView(APIView):
    """
    GET /api/v1/admin/transactions/stats
    Retourne les indicateurs de performance clés (KPI) pour le tableau de bord des paiements.
    """
    permission_classes = [IsSuperAdmin]

    @extend_schema(
        tags=['Paiements'],
        summary='Statistiques des transactions de paiement',
        description='Calcule le total par jour, le montant total, le taux de succès et la répartition par type.'
    )
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        today = now.date()

        # Nombre total de transactions créées aujourd'hui
        total_today = PaymentTransaction.objects.filter(created_at__date=today).count()

        # Montant total cumulé de toutes les transactions réussies
        total_amount = PaymentTransaction.objects.filter(status=PaymentStatus.SUCCESS).aggregate(total=Sum('amount'))['total'] or 0.0

        # Taux de succès global
        total_count = PaymentTransaction.objects.count()
        success_count = PaymentTransaction.objects.filter(status=PaymentStatus.SUCCESS).count()
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0.0

        # Répartition par type de paiement
        distribution = list(
            PaymentTransaction.objects.values('payment_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        dist_dict = {item['payment_type']: item['count'] for item in distribution}

        return success_response({
            'total_today': total_today,
            'total_amount': float(total_amount),
            'success_rate': round(success_rate, 2),
            'distribution': dist_dict
        })

