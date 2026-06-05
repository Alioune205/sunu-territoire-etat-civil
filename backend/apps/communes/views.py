"""
Views for Commune management.
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.shared.permissions import IsSuperAdmin
from apps.shared.responses import success_response

from .models import Commune
from .serializers import CommuneSerializer, CommuneListSerializer


@extend_schema_view(
    list=extend_schema(tags=['Communes'], summary='Lister les communes'),
    retrieve=extend_schema(tags=['Communes'], summary='Détail d\'une commune'),
    create=extend_schema(tags=['Communes'], summary='Créer une commune'),
    update=extend_schema(tags=['Communes'], summary='Modifier une commune'),
    partial_update=extend_schema(tags=['Communes'], summary='Modifier partiellement une commune'),
    destroy=extend_schema(tags=['Communes'], summary='Supprimer une commune'),
)
class CommuneViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Communes.
    - List/Retrieve: Public access (AllowAny)
    - Create/Update/Delete: Super admin only
    """
    queryset = Commune.objects.all()
    filterset_fields = ['region', 'department', 'is_active']
    search_fields = ['name', 'region', 'department', 'code']
    ordering_fields = ['name', 'region', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return CommuneListSerializer
        return CommuneSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsSuperAdmin()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)
