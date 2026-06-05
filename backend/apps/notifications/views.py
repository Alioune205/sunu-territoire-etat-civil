"""
Notifications views for managing FCM tokens and viewing history.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, extend_schema_view

from django.contrib.auth import get_user_model

from apps.shared.permissions import IsAdminStaff, IsSuperAdmin
from apps.shared.responses import success_response, error_response
from apps.shared.pagination import StandardPagination

from .models import Notification, NotificationToken
from .serializers import (
    NotificationSerializer,
    NotificationTokenSerializer,
    SendNotificationSerializer,
)
from .services import send_fcm_notification

User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=['Notifications'], summary="Historique des notifications de l'utilisateur"),
)
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to view notification history and perform notification actions.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filterset_fields = ['is_read', 'type']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'send_notification':
            return [IsAuthenticated(), (IsAdminStaff | IsSuperAdmin)()]
        return super().get_permissions()

    def get_queryset(self):
        # Users only see their own notifications
        return Notification.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)

    # =====================================================
    # ACTIONS
    # =====================================================

    @extend_schema(tags=['Notifications'], summary="Marquer une notification comme lue")
    @action(detail=True, methods=['post'], url_path='read')
    def mark_as_read(self, request, pk=None):
        """POST /api/notifications/{id}/read/"""
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read', 'updated_at'])
        return success_response(
            data=NotificationSerializer(notification).data,
            message="Notification marquée comme lue."
        )

    @extend_schema(tags=['Notifications'], summary="Marquer toutes les notifications comme lues")
    @action(detail=False, methods=['post'], url_path='read-all')
    def mark_all_as_read(self, request):
        """POST /api/notifications/read-all/"""
        unread = self.get_queryset().filter(is_read=False)
        count = unread.update(is_read=True)
        return success_response(
            message=f"{count} notification(s) marquée(s) comme lues."
        )

    @extend_schema(
        tags=['Notifications'],
        summary="Enregistrer ou mettre à jour un token FCM",
        request=NotificationTokenSerializer,
        responses={201: NotificationTokenSerializer}
    )
    @action(detail=False, methods=['post'], url_path='tokens')
    def register_token(self, request):
        """POST /api/notifications/tokens/"""
        serializer = NotificationTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        token_obj = serializer.save()
        return success_response(
            data=NotificationTokenSerializer(token_obj).data,
            message="Token FCM enregistré avec succès.",
            status_code=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=['Notifications'],
        summary="Envoyer une notification push (Admin uniquement)",
        request=SendNotificationSerializer,
        responses={201: NotificationSerializer}
    )
    @action(
        detail=False,
        methods=['post'],
        url_path='send',
        permission_classes=[IsAuthenticated, IsAdminStaff | IsSuperAdmin]
    )
    def send_notification(self, request):
        """POST /api/notifications/send/"""
        # Explicit role check for safety (required when viewset is mapped manually in urls.py)
        if not (request.user.role in ['reception_agent', 'verification_agent', 'civil_admin', 'super_admin']):
            return error_response(
                message="Accès réservé au personnel administratif.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(id=serializer.validated_data['user_id'])
        notification = send_fcm_notification(
            user=user,
            title=serializer.validated_data['title'],
            body=serializer.validated_data['body'],
            notification_type=serializer.validated_data['type'],
            data=serializer.validated_data.get('data', {})
        )

        return success_response(
            data=NotificationSerializer(notification).data,
            message="Notification envoyée et enregistrée.",
            status_code=status.HTTP_201_CREATED,
        )
