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


import random
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from apps.users.models import OTPCode, User
from .serializers import SendOTPSerializer, VerifyOTPSerializer
from rest_framework.throttling import ScopedRateThrottle

class SendOTPView(GenericAPIView):
    """
    POST /api/auth/otp/send/
    """
    serializer_class = SendOTPSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp'

    @extend_schema(
        tags=['Auth'],
        summary='Demander un code OTP',
        responses={200: OpenApiResponse(description='Code OTP envoyé')},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['identifier']

        code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)

        OTPCode.objects.create(identifier=identifier, code=code, expires_at=expires_at)
        print(f"\\n{'='*40}\\n[SIMULATION OTP] Code pour {identifier} : {code}\\n{'='*40}\\n")

        return success_response(message='Code OTP envoyé avec succès.')


class VerifyOTPView(GenericAPIView):
    """
    POST /api/auth/otp/verify/
    """
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    @extend_schema(
        tags=['Auth'],
        summary='Vérifier un code OTP',
        responses={200: OpenApiResponse(description='Connexion réussie')},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        otp = serializer.validated_data['otp']
        identifier = serializer.validated_data['identifier']
        
        otp.is_used = True
        otp.save()
        
        user = User.objects.filter(Q(email=identifier) | Q(phone=identifier)).first()
        if user:
            if not user.is_verified:
                user.is_verified = True
                user.save()
            
            # Log history
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT')
            from apps.users.models import LoginHistory
            LoginHistory.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )

            refresh = RefreshToken.for_user(user)
            
            return success_response(
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
                message='Code OTP vérifié et connexion réussie.',
            )

        return error_response(message='Utilisateur introuvable.', status_code=status.HTTP_404_NOT_FOUND)


from .serializers import LoginHistorySerializer
from apps.users.models import LoginHistory

class LoginHistoryView(GenericAPIView):
    """
    GET /api/auth/login-history/
    """
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Historique des connexions',
        responses={200: LoginHistorySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        history = LoginHistory.objects.filter(user=request.user)[:50]
        serializer = self.get_serializer(history, many=True)
        return success_response(data=serializer.data, message='Historique récupéré.')
