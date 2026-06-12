"""
Serializers for Dossier and DossierComment.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.communes.models import Commune
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
    commune = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Commune.objects.all(),
        error_messages={'does_not_exist': 'Commune introuvable avec ce code.'}
    )

    class Meta:
        model = Dossier
        fields = [
            'id',
            'type',
            'commune',
            'notes',
            'is_for_third_party',
            'third_party_cni',
            'third_party_relation',
            'metadata',
        ]
        read_only_fields = ['id']

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
            'is_for_third_party',
            'metadata',
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
            'is_for_third_party',
            'third_party_cni',
            'third_party_relation',
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
        fields = ['notes']


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
