"""
Views for Dossier management with workflow actions.
"""
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse

from django.contrib.auth import get_user_model

from apps.shared.permissions import (
    IsCitizen,
    IsAdminStaff,
    IsCivilAdmin,
)
from apps.shared.responses import success_response, error_response

from .models import Dossier, RegistreCivil
from .serializers import (
    DossierCreateSerializer,
    DossierListSerializer,
    DossierDetailSerializer,
    DossierUpdateSerializer,
    DossierCommentSerializer,
    DossierAssignSerializer,
    DossierRejectSerializer,
)

User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=['Dossiers'], summary='Lister les dossiers'),
    retrieve=extend_schema(tags=['Dossiers'], summary='Détail d\'un dossier'),
    create=extend_schema(tags=['Dossiers'], summary='Créer un dossier'),
    partial_update=extend_schema(tags=['Dossiers'], summary='Modifier un dossier'),
)
class DossierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for dossier management.
    Citizens see their own dossiers; agents see dossiers from their commune.
    """
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_fields = ['type', 'status', 'commune']
    search_fields = ['reference', 'citizen__first_name', 'citizen__last_name']
    ordering_fields = ['created_at', 'submitted_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Dossier.objects.select_related(
            'citizen', 'assigned_agent', 'commune'
        ).prefetch_related('comments', 'documents')

        if user.role == 'citizen':
            return qs.filter(citizen=user)
        elif user.is_admin_staff and user.commune:
            return qs.filter(commune=user.commune)
        elif user.role == 'super_admin':
            return qs.all()
        return qs.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return DossierCreateSerializer
        if self.action == 'list':
            return DossierListSerializer
        if self.action == 'partial_update':
            return DossierUpdateSerializer
        return DossierDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsCitizen()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dossier = serializer.save()
        return success_response(
            data=DossierDetailSerializer(dossier).data,
            message='Dossier créé avec succès.',
            status_code=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Citizens can only edit drafts
        if request.user.role == 'citizen' and instance.status != 'draft':
            return error_response(
                message='Vous ne pouvez modifier un dossier que s\'il est en brouillon.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
        if request.user.role == 'citizen' and instance.citizen != request.user:
            return error_response(
                message='Accès interdit.',
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=DossierDetailSerializer(instance).data,
            message='Dossier mis à jour avec succès.',
        )

    @extend_schema(
        tags=['Dossiers'],
        summary="Vérifier l'existence d'un acte dans le Registre Civil",
        description="Vérifie si le numéro et l'année existent. Valide aussi la correspondance du nom ou de la CNI.",
        responses={
            200: OpenApiResponse(description='Acte trouvé et vérifié. Veuillez demander la date de naissance pour confirmer.'),
            400: OpenApiResponse(description='Acte non trouvé ou non correspondant.'),
        },
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsCitizen], url_path='verify-registry')
    def verify_registry(self, request):
        """POST /api/dossiers/verify-registry/"""
        user = request.user
        
        numero_registre = request.data.get('numero_registre')
        annee_registre = request.data.get('annee_registre')
        commune_id = request.data.get('commune')
        type_acte = request.data.get('type_acte')
        is_for_third_party = str(request.data.get('is_for_third_party', 'false')).lower() == 'true'

        if not all([numero_registre, annee_registre, commune_id, type_acte]):
            return error_response(
                message='numero_registre, annee_registre, commune et type_acte sont obligatoires.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Chercher dans la base simulée
        try:
            registre = RegistreCivil.objects.get(
                numero_registre=numero_registre,
                annee_registre=annee_registre,
                commune_id=commune_id,
                type_acte=type_acte
            )
        except RegistreCivil.DoesNotExist:
            return error_response(
                message='Cet acte est introuvable dans le Registre Civil.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Si tierce personne, exiger CNI du demandeur, pas besoin de vérifier le nom de l'acte contre le demandeur.
        if is_for_third_party:
            if not hasattr(user, 'profile') or not user.profile.cni_number:
                return error_response(
                    message='Votre profil doit contenir un numéro de CNI valide pour faire une demande pour autrui.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Demande personnelle : vérifier que le nom correspond à l'utilisateur connecté
            user_nom = user.full_name.lower().strip()
            registre_nom = f"{registre.prenoms_enfant} {registre.nom_enfant}".lower().strip()
            
            # Simple vérification (dans la vraie vie on utilise des algorithmes phonétiques)
            if user_nom not in registre_nom and registre_nom not in user_nom:
                return error_response(
                    message='Les noms sur cet acte ne correspondent pas à votre identité.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        return success_response(
            message='Acte trouvé. Veuillez fournir la date de naissance pour valider la demande.'
        )

    # =====================================================
    # WORKFLOW ACTIONS
    # =====================================================

    @extend_schema(tags=['Dossiers'], summary='Soumettre un dossier')
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        """POST /api/dossiers/{id}/submit/ — Submit a draft dossier."""
        dossier = self.get_object()

        if dossier.citizen != request.user:
            return error_response(
                message='Seul le propriétaire peut soumettre ce dossier.',
                status_code=status.HTTP_403_FORBIDDEN,
            )
        if dossier.status != Dossier.Status.DRAFT:
            return error_response(
                message='Seul un dossier en brouillon peut être soumis.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        dossier.status = Dossier.Status.SUBMITTED
        dossier.submitted_at = timezone.now()
        dossier.save(update_fields=['status', 'submitted_at', 'updated_at'])

        return success_response(
            data=DossierDetailSerializer(dossier).data,
            message='Dossier soumis avec succès.',
        )

    @extend_schema(tags=['Dossiers'], summary='Assigner un agent', request=DossierAssignSerializer)
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminStaff])
    def assign(self, request, pk=None):
        """POST /api/dossiers/{id}/assign/ — Assign an agent."""
        dossier = self.get_object()
        serializer = DossierAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        agent = User.objects.get(id=serializer.validated_data['agent_id'])
        dossier.assigned_agent = agent
        dossier.save(update_fields=['assigned_agent', 'updated_at'])

        return success_response(
            data=DossierDetailSerializer(dossier).data,
            message=f'Dossier assigné à {agent.full_name}.',
        )

    @extend_schema(tags=['Dossiers'], summary='Mettre en vérification')
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminStaff])
    def review(self, request, pk=None):
        """POST /api/dossiers/{id}/review/ — Move to in_review."""
        dossier = self.get_object()

        if dossier.status != Dossier.Status.SUBMITTED:
            return error_response(
                message='Seul un dossier soumis peut être mis en vérification.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        dossier.status = Dossier.Status.IN_REVIEW
        dossier.reviewed_at = timezone.now()
        dossier.save(update_fields=['status', 'reviewed_at', 'updated_at'])

        return success_response(
            data=DossierDetailSerializer(dossier).data,
            message='Dossier mis en cours de vérification.',
        )

    @extend_schema(tags=['Dossiers'], summary='Approuver un dossier')
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsCivilAdmin])
    def approve(self, request, pk=None):
        """POST /api/dossiers/{id}/approve/ — Approve the dossier and generate signed certificate."""
        dossier = self.get_object()

        if dossier.status not in [Dossier.Status.IN_REVIEW, Dossier.Status.GENERATED]:
            return error_response(
                message='Seul un dossier en vérification ou généré peut être approuvé.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        dossier.status = Dossier.Status.VALIDATED
        dossier.completed_at = timezone.now()
        dossier.save(update_fields=['status', 'completed_at', 'updated_at'])

        # Génération du certificat PDF signé cryptographiquement
        from apps.dossiers.services.pdf_generator import generate_signed_certificate
        try:
            cert = generate_signed_certificate(dossier, officier=request.user)
            msg = (
                f'Dossier approuvé. Certificat {cert.dossier.reference} généré '
                f'avec signature HMAC et timbre {cert.timbre.reference}.'
            )
        except Exception as e:
            msg = f'Dossier approuvé, mais erreur lors de la génération du certificat : {str(e)}'

        return success_response(
            data=DossierDetailSerializer(dossier).data,
            message=msg,
        )

    @extend_schema(tags=['Dossiers'], summary='Rejeter un dossier', request=DossierRejectSerializer)
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsCivilAdmin])
    def reject(self, request, pk=None):
        """POST /api/dossiers/{id}/reject/ — Reject with reason."""
        dossier = self.get_object()
        serializer = DossierRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if dossier.status != Dossier.Status.IN_REVIEW:
            return error_response(
                message='Seul un dossier en vérification peut être rejeté.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        dossier.status = Dossier.Status.REJECTED
        dossier.rejection_reason = serializer.validated_data['rejection_reason']
        dossier.completed_at = timezone.now()
        dossier.save(update_fields=['status', 'rejection_reason', 'completed_at', 'updated_at'])

        return success_response(
            data=DossierDetailSerializer(dossier).data,
            message='Dossier rejeté.',
        )

    @extend_schema(tags=['Dossiers'], summary='Terminer un dossier')
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsCivilAdmin])
    def complete(self, request, pk=None):
        """POST /api/dossiers/{id}/complete/ — Mark as completed."""
        dossier = self.get_object()

        if dossier.status != Dossier.Status.APPROVED:
            return error_response(
                message='Seul un dossier approuvé peut être marqué comme terminé.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        dossier.status = Dossier.Status.COMPLETED
        dossier.save(update_fields=['status', 'updated_at'])

        return success_response(
            data=DossierDetailSerializer(dossier).data,
            message='Dossier marqué comme terminé.',
        )

    # =====================================================
    # COMMENTS
    # =====================================================

    @extend_schema(tags=['Dossiers'], summary='Commentaires du dossier')
    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        """GET/POST /api/dossiers/{id}/comments/"""
        dossier = self.get_object()

        if request.method == 'GET':
            comments = dossier.comments.select_related('author').all()
            serializer = DossierCommentSerializer(comments, many=True)
            return success_response(data=serializer.data)

        # POST
        serializer = DossierCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(dossier=dossier, author=request.user)
        return success_response(
            data=serializer.data,
            message='Commentaire ajouté.',
            status_code=status.HTTP_201_CREATED,
        )
