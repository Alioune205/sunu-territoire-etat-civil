"""
RBAC Permission classes for TERANGA CIVIL.
These permissions check the user's role field for access control.
"""
from rest_framework.permissions import BasePermission


class IsRole(BasePermission):
    """
    Base permission class that checks if a user has one of the allowed roles.
    Subclass this and set `allowed_roles` to define specific role permissions.
    """
    allowed_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in self.allowed_roles


class IsCitizen(IsRole):
    """Only citizens can access."""
    allowed_roles = ['citizen']
    message = 'Accès réservé aux citoyens.'


class IsReceptionAgent(IsRole):
    """Only reception agents can access."""
    allowed_roles = ['reception_agent']
    message = 'Accès réservé aux agents de réception.'


class IsVerificationAgent(IsRole):
    """Only verification agents can access."""
    allowed_roles = ['verification_agent']
    message = 'Accès réservé aux agents de vérification.'


class IsCivilAdmin(IsRole):
    """Only civil administrators can access."""
    allowed_roles = ['civil_admin']
    message = 'Accès réservé aux administrateurs d\'état civil.'


class IsSuperAdmin(IsRole):
    """Only super administrators can access."""
    allowed_roles = ['super_admin']
    message = 'Accès réservé aux super administrateurs.'


class IsAdminStaff(IsRole):
    """
    Any administrative staff (reception_agent, verification_agent,
    civil_admin, super_admin) can access.
    """
    allowed_roles = [
        'reception_agent',
        'verification_agent',
        'civil_admin',
        'super_admin',
    ]
    message = 'Accès réservé au personnel administratif.'


class IsAdminOrReadOnly(BasePermission):
    """
    Admin staff gets full access; others get read-only.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return request.method in ('GET', 'HEAD', 'OPTIONS')

        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        return request.user.role in [
            'reception_agent',
            'verification_agent',
            'civil_admin',
            'super_admin',
        ]


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: owner of the object or admin staff.
    The object must have a `user` or `citizen` field pointing to the User.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is admin staff
        if request.user.role in ['civil_admin', 'super_admin']:
            return True

        # Check ownership via common FK names
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        if hasattr(obj, 'citizen') and obj.citizen == request.user:
            return True
        if hasattr(obj, 'uploaded_by') and obj.uploaded_by == request.user:
            return True

        return False
