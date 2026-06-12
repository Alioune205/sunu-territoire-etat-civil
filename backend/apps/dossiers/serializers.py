"""
Serializers for Dossier and DossierComment.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Dossier, DossierComment

User = get_user_model()


class DossierCommentSerializer(serializers.ModelSerializer):
    """Serializer for dossier comments."""
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_role = serializers.CharField(source='author.role', read_only=True)

    class Meta:
        model = DossierComment
        fields = [
            'id',
            'dossier',
            'author',
            'author_name',
            'author_role',
            'content',
            'created_at',
        ]
        read_only_fields = ['id', 'author', 'author_name', 'author_role', 'created_at']


class DossierCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a dossier."""

    class Meta:
        model = Dossier
        fields = [
            'type',
            'commune',
            'notes',
            'metadata',
        ]

    def validate(self, attrs):
        dossier_type = attrs.get('type')
        metadata = attrs.get('metadata', {})
        
        from datetime import datetime, timedelta
        
        # Validations métier pour les nouveaux actes (Tâche 8 : Pièces jointes JSON)
        if dossier_type == Dossier.Type.RESIDENCE_CERTIFICATE:
            if not metadata.get('cni_recto') or not metadata.get('attestation_delegue'):
                raise serializers.ValidationError("Pour un certificat de résidence, le payload JSON doit contenir 'cni_recto' et 'attestation_delegue'.")
                
        elif dossier_type == Dossier.Type.DEATH_CERTIFICATE:
            if not metadata.get('constat_medecin') or not metadata.get('cni_defunt'):
                raise serializers.ValidationError("Pour un acte de décès, le payload JSON doit contenir 'constat_medecin' et 'cni_defunt'.")
            
            # Tâche 7 : Blocage de délai (date_deces <= 1 an)
            date_deces_str = metadata.get('date_deces')
            if not date_deces_str:
                raise serializers.ValidationError("La 'date_deces' est requise pour un acte de décès.")
            try:
                date_deces = datetime.strptime(date_deces_str, "%Y-%m-%d").date()
                if (datetime.now().date() - date_deces).days > 365:
                    raise serializers.ValidationError("Un acte de décès ne peut être établi si la date de décès remonte à plus d'un an.")
            except ValueError:
                raise serializers.ValidationError("Le format de 'date_deces' doit être YYYY-MM-DD.")
                
        elif dossier_type == Dossier.Type.MARRIAGE_CERTIFICATE:
            if not metadata.get('cni_epoux') or not metadata.get('cni_epouse') or not metadata.get('cni_temoins'):
                raise serializers.ValidationError("Pour un acte de mariage, le payload JSON doit contenir 'cni_epoux', 'cni_epouse' et 'cni_temoins'.")

        return attrs

    def create(self, validated_data):
        validated_data['citizen'] = self.context['request'].user
        validated_data['status'] = Dossier.Status.DRAFT
        return super().create(validated_data)


class DossierListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dossier lists."""
    citizen_name = serializers.CharField(source='citizen.full_name', read_only=True)
    agent_name = serializers.CharField(source='assigned_agent.full_name', read_only=True, default=None)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    commune_name = serializers.CharField(source='commune.name', read_only=True)

    class Meta:
        model = Dossier
        fields = [
            'id',
            'reference',
            'type',
            'type_display',
            'status',
            'status_display',
            'citizen',
            'citizen_name',
            'assigned_agent',
            'agent_name',
            'commune',
            'commune_name',
            'submitted_at',
            'created_at',
        ]
        read_only_fields = fields


class DossierDetailSerializer(serializers.ModelSerializer):
    """Full serializer for dossier detail with comments."""
    citizen_name = serializers.CharField(source='citizen.full_name', read_only=True)
    citizen_email = serializers.CharField(source='citizen.email', read_only=True)
    agent_name = serializers.CharField(source='assigned_agent.full_name', read_only=True, default=None)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    commune_name = serializers.CharField(source='commune.name', read_only=True)
    comments = DossierCommentSerializer(many=True, read_only=True)
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = Dossier
        fields = [
            'id',
            'reference',
            'type',
            'type_display',
            'status',
            'status_display',
            'citizen',
            'citizen_name',
            'citizen_email',
            'assigned_agent',
            'agent_name',
            'commune',
            'commune_name',
            'notes',
            'metadata',
            'rejection_reason',
            'submitted_at',
            'reviewed_at',
            'completed_at',
            'comments',
            'document_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_document_count(self, obj):
        return obj.documents.count() if hasattr(obj, 'documents') else 0


class DossierUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating dossier (limited fields)."""

    class Meta:
        model = Dossier
        fields = ['notes', 'metadata']
        
    def validate(self, attrs):
        # Valider également lors de l'update si metadata est fourni
        if 'metadata' in attrs:
            instance = getattr(self, 'instance', None)
            dossier_type = instance.type if instance else attrs.get('type')
            metadata = attrs.get('metadata', {})
            
            from datetime import datetime
            if dossier_type == Dossier.Type.RESIDENCE_CERTIFICATE:
                if not metadata.get('cni_recto') or not metadata.get('attestation_delegue'):
                    raise serializers.ValidationError("Pour un certificat de résidence, le payload JSON doit contenir 'cni_recto' et 'attestation_delegue'.")
                    
            elif dossier_type == Dossier.Type.DEATH_CERTIFICATE:
                if not metadata.get('constat_medecin') or not metadata.get('cni_defunt'):
                    raise serializers.ValidationError("Pour un acte de décès, le payload JSON doit contenir 'constat_medecin' et 'cni_defunt'.")
                
                date_deces_str = metadata.get('date_deces')
                if not date_deces_str:
                    raise serializers.ValidationError("La 'date_deces' est requise pour un acte de décès.")
                try:
                    date_deces = datetime.strptime(date_deces_str, "%Y-%m-%d").date()
                    if (datetime.now().date() - date_deces).days > 365:
                        raise serializers.ValidationError("Un acte de décès ne peut être établi si la date de décès remonte à plus d'un an.")
                except ValueError:
                    raise serializers.ValidationError("Le format de 'date_deces' doit être YYYY-MM-DD.")
                    
            elif dossier_type == Dossier.Type.MARRIAGE_CERTIFICATE:
                if not metadata.get('cni_epoux') or not metadata.get('cni_epouse') or not metadata.get('cni_temoins'):
                    raise serializers.ValidationError("Pour un acte de mariage, le payload JSON doit contenir 'cni_epoux', 'cni_epouse' et 'cni_temoins'.")

        return attrs


class DossierAssignSerializer(serializers.Serializer):
    """Serializer for assigning an agent to a dossier."""
    agent_id = serializers.UUIDField(required=True)

    def validate_agent_id(self, value):
        try:
            agent = User.objects.get(id=value)
            if agent.role not in ['reception_agent', 'verification_agent', 'civil_admin', 'super_admin']:
                raise serializers.ValidationError(
                    'L\'utilisateur n\'est pas un agent administratif.'
                )
        except User.DoesNotExist:
            raise serializers.ValidationError('Agent non trouvé.')
        return value


class DossierRejectSerializer(serializers.Serializer):
    """Serializer for rejecting a dossier with reason."""
    rejection_reason = serializers.CharField(required=True, min_length=10)
