"""
Views for Document management.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.shared.permissions import IsOwnerOrAdmin, IsCivilAdmin
from apps.shared.responses import success_response, error_response

from .models import Document
from .serializers import (
    DocumentSerializer,
    DocumentUploadSerializer,
    DocumentListSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=['Documents'], summary='Lister les documents'),
    retrieve=extend_schema(tags=['Documents'], summary='Détail d\'un document'),
    create=extend_schema(tags=['Documents'], summary='Téléverser un document'),
    destroy=extend_schema(tags=['Documents'], summary='Supprimer un document'),
)
class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for document management.
    - Upload: Authenticated users
    - List/Retrieve: Owner or admin staff
    - Delete: Owner or civil admin
    """
    http_method_names = ['get', 'post', 'delete']
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['dossier', 'file_type', 'ocr_status']
    search_fields = ['original_filename', 'description']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Document.objects.select_related('dossier', 'uploaded_by')

        if user.role == 'citizen':
            return qs.filter(dossier__citizen=user)
        elif user.is_admin_staff and user.commune:
            return qs.filter(dossier__commune=user.commune)
        elif user.role == 'super_admin':
            return qs.all()
        return qs.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentUploadSerializer
        if self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        return success_response(
            data=DocumentSerializer(document).data,
            message='Document téléversé avec succès.',
            status_code=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Only owner or civil_admin can delete
        if (instance.uploaded_by != request.user and
                request.user.role not in ['civil_admin', 'super_admin']):
            return error_response(
                message='Accès interdit.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
        instance.delete()
        return success_response(message='Document supprimé avec succès.')
