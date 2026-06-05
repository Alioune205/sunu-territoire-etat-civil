"""
Views for JWT authentication: login, register, refresh, logout.
"""
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.shared.responses import success_response, error_response, created_response

from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    LogoutSerializer,
)


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/

    Authenticate a user and return JWT access + refresh tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Connexion utilisateur',
        description='Authentifie un utilisateur et retourne les tokens JWT.',
        responses={
            200: OpenApiResponse(description='Connexion réussie'),
            401: OpenApiResponse(description='Identifiants invalides'),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return error_response(
                message='Email ou mot de passe incorrect.',
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return success_response(
            data=serializer.validated_data,
            message='Connexion réussie.',
        )


class RegisterView(GenericAPIView):
    """
    POST /api/auth/register/

    Register a new citizen user.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Inscription citoyen',
        description='Crée un nouveau compte citoyen et retourne les tokens JWT.',
        responses={
            201: OpenApiResponse(description='Inscription réussie'),
            400: OpenApiResponse(description='Données invalides'),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)

        return created_response(
            data={
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name,
                    'role': user.role,
                    'is_verified': user.is_verified,
                },
            },
            message='Inscription réussie.',
        )


class CustomTokenRefreshView(TokenRefreshView):
    """
    POST /api/auth/refresh/

    Refresh an access token using a valid refresh token.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Rafraîchir le token',
        description='Génère un nouveau token d\'accès à partir du refresh token.',
        responses={
            200: OpenApiResponse(description='Token rafraîchi'),
            401: OpenApiResponse(description='Refresh token invalide'),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return error_response(
                message='Token de rafraîchissement invalide ou expiré.',
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return success_response(
            data=serializer.validated_data,
            message='Token rafraîchi avec succès.',
        )


class LogoutView(GenericAPIView):
    """
    POST /api/auth/logout/

    Blacklist the refresh token to log the user out.
    """
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Déconnexion',
        description='Invalide le refresh token pour déconnecter l\'utilisateur.',
        responses={
            200: OpenApiResponse(description='Déconnexion réussie'),
            400: OpenApiResponse(description='Token invalide'),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
        except TokenError:
            return error_response(
                message='Token invalide ou déjà révoqué.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return success_response(message='Déconnexion réussie.')
