"""
Notifications views.
"""
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import FCMDevice, Notification
from .serializers import FCMDeviceSerializer, NotificationSerializer

@extend_schema(tags=['Notifications'])
class FCMDeviceViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    Manage FCM devices for the authenticated user.
    """
    serializer_class = FCMDeviceSerializer
    
    def get_queryset(self):
        return FCMDevice.objects.filter(user=self.request.user)

@extend_schema(tags=['Notifications'])
class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    View and manage notifications for the authenticated user.
    """
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @extend_schema(
        summary="Mark notification as read",
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(self.get_serializer(notification).data)

    @extend_schema(
        summary="Mark all notifications as read",
        responses={200: {"type": "object", "properties": {"status": {"type": "string"}}}}
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"status": "All notifications marked as read"})
