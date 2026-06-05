"""
Services views — API endpoints pour Paiements, Signalements, Sondages.
"""
from django.utils import timezone
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.shared.permissions import IsCitizen, IsAdminStaff
from apps.shared.responses import success_response, error_response
from apps.integrations.payment_mock import PaymentGatewayMock

from .models import Transaction, Report, Survey, SurveyOption, SurveyVote
from .serializers import (
    TransactionSerializer,
    ReportSerializer,
    ReportAdminUpdateSerializer,
    SurveySerializer,
    SurveyVoteSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=['Services - Paiements']),
    retrieve=extend_schema(tags=['Services - Paiements']),
    create=extend_schema(tags=['Services - Paiements']),
)
class TransactionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Gestion des transactions de paiement pour les dossiers.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'citizen':
            return Transaction.objects.filter(citizen=user)
        return Transaction.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()

        # Initier le paiement via le mock
        payment_mock = PaymentGatewayMock()
        payment_response = payment_mock.initiate_payment(
            amount=transaction.amount,
            phone_number=transaction.phone_number,
            provider=transaction.provider
        )

        transaction.external_transaction_id = payment_response.get("transaction_id", "")
        transaction.save()

        return success_response(
            data=TransactionSerializer(transaction).data,
            message='Paiement initié.',
            status_code=status.HTTP_201_CREATED
        )

    @extend_schema(tags=['Services - Paiements'], summary="Vérifier le statut du paiement")
    @action(detail=True, methods=['post'])
    def check_status(self, request, pk=None):
        transaction = self.get_object()
        
        if transaction.status == Transaction.Status.PENDING:
            payment_mock = PaymentGatewayMock()
            status_response = payment_mock.check_transaction_status(transaction.external_transaction_id)
            if status_response.get("status") == "completed":
                transaction.status = Transaction.Status.COMPLETED
                transaction.paid_at = timezone.now()
                transaction.receipt_url = f"https://mock.receipts.local/{status_response.get('receipt_number')}"
                transaction.save()

        return success_response(data=TransactionSerializer(transaction).data)


@extend_schema_view(
    list=extend_schema(tags=['Services - Signalements']),
    retrieve=extend_schema(tags=['Services - Signalements']),
    create=extend_schema(tags=['Services - Signalements']),
)
class ReportViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Signalements citoyens (voirie, déchets, etc.).
    """
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'citizen':
            return Report.objects.filter(citizen=user)
        elif user.is_admin_staff and user.commune:
            return Report.objects.filter(commune=user.commune)
        elif user.role == 'super_admin':
            return Report.objects.all()
        return Report.objects.none()

    @extend_schema(tags=['Services - Signalements'], summary="Mettre à jour le statut du signalement", request=ReportAdminUpdateSerializer)
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdminStaff])
    def update_status(self, request, pk=None):
        report = self.get_object()
        serializer = ReportAdminUpdateSerializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=ReportSerializer(report).data, message="Signalement mis à jour.")


@extend_schema_view(
    list=extend_schema(tags=['Services - Sondages']),
    retrieve=extend_schema(tags=['Services - Sondages']),
)
class SurveyViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Sondages et consultations citoyennes.
    """
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_staff and user.commune:
            return Survey.objects.filter(commune=user.commune)
        elif user.role == 'citizen' and user.commune:
            return Survey.objects.filter(commune=user.commune)
        return Survey.objects.all()

    @extend_schema(tags=['Services - Sondages'], summary="Voter à un sondage", request=SurveyVoteSerializer)
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsCitizen])
    def vote(self, request, pk=None):
        survey = self.get_object()
        data = request.data.copy()
        data['survey'] = survey.id
        
        serializer = SurveyVoteSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        option = serializer.validated_data['option']
        
        # Save vote and update count
        SurveyVote.objects.create(survey=survey, option=option, citizen=request.user)
        option.votes_count += 1
        option.save()
        
        return success_response(message="Votre vote a été enregistré.")
