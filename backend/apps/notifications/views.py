"""
Views for Notifications.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

# pyrefly: ignore [missing-import]
from apps.shared.permissions import IsAdminStaff
# pyrefly: ignore [missing-import]
from apps.shared.responses import success_response

from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Notification, DeviceToken
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications."""

    queryset = Notification.objects.select_related('user').all()
    serializer_class = NotificationSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdminStaff()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) in [
            'civil_admin', 'super_admin',
            'verification_agent', 'reception_agent'
        ]:
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save()

    @extend_schema(
        tags=['Notifications'],
        summary='Marquer une notification comme lue',
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        return success_response(
            data=NotificationSerializer(notification).data,
            message='Notification marquée comme lue.',
        )

    @extend_schema(
        tags=['Notifications'],
        summary='Lister les notifications',
        responses={200: NotificationSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        notification = self.get_object()
        serializer = self.get_serializer(notification)
        return success_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            data=serializer.data,
            message='Notification créée avec succès.',
            status_code=status.HTTP_201_CREATED,
        )


class RegisterDeviceView(APIView):
    """API for registering FCM device tokens."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        device_type = request.data.get('device_type', '')

        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        device_token, created = DeviceToken.objects.update_or_create(
            token=token,
            defaults={
                'user': request.user,
                'device_type': device_type
            }
        )

        return success_response(
            data={'token': device_token.token, 'created': created},
            message='Token enregistré avec succès.'
        )
