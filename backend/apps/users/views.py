"""
Views for User and CitizenProfile management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..shared.permissions import IsAdminStaff, IsSuperAdmin
from ..shared.responses import success_response, error_response

from .models import User, CitizenProfile
from .serializers import (
    UserSerializer,
    UserListSerializer,
    UserUpdateSerializer,
    CitizenProfileSerializer,
    CitizenProfileDetailSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    - List: Admin staff only (filterable by role, commune)
    - Retrieve: Owner or admin staff
    - Update: Owner (limited) or super admin (full)
    - Delete: Super admin only
    """
    queryset = User.objects.select_related('commune').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'commune', 'is_verified', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['created_at', 'first_name', 'last_name', 'email']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        if self.action in ('update', 'partial_update'):
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated(), IsAdminStaff()]
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        if self.action in ('update', 'partial_update'):
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated(), IsAdminStaff()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Allow owner or admin
        if instance != request.user and not request.user.is_admin_staff:
            return error_response(
                message='Accès interdit.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Only owner or super_admin can update
        if instance != request.user and request.user.role != 'super_admin':
            return error_response(
                message='Accès interdit.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=UserSerializer(instance).data,
            message='Utilisateur mis à jour avec succès.',
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get the current authenticated user's data."""
        serializer = UserSerializer(request.user)
        return success_response(data=serializer.data)


class CitizenProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing citizen profiles.
    - List: Admin staff only
    - Retrieve/Update: Owner or admin staff
    """
    queryset = CitizenProfile.objects.select_related('user').all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['gender']
    search_fields = ['user__first_name', 'user__last_name', 'cni_number']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CitizenProfileDetailSerializer
        return CitizenProfileSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated(), IsAdminStaff()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_admin_staff:
            return error_response(
                message='Accès interdit.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and request.user.role != 'super_admin':
            return error_response(
                message='Accès interdit.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=CitizenProfileDetailSerializer(instance).data,
            message='Profil mis à jour avec succès.',
        )

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get or update the current user's profile."""
        try:
            profile = CitizenProfile.objects.select_related('user').get(user=request.user)
        except CitizenProfile.DoesNotExist:
            return error_response(
                message='Profil citoyen non trouvé.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if request.method == 'GET':
            serializer = CitizenProfileDetailSerializer(profile)
            return success_response(data=serializer.data)

        # PATCH
        serializer = CitizenProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=CitizenProfileDetailSerializer(profile).data,
            message='Profil mis à jour avec succès.',
        )
