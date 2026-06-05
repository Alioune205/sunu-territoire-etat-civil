"""
Serializers for Commune.
"""
from rest_framework import serializers
from .models import Commune


class CommuneSerializer(serializers.ModelSerializer):
    """Full serializer for Commune."""

    class Meta:
        model = Commune
        fields = [
            'id',
            'name',
            'region',
            'department',
            'code',
            'address',
            'phone',
            'email',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommuneListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for commune lists."""

    class Meta:
        model = Commune
        fields = ['id', 'name', 'region', 'department', 'code', 'is_active']
        read_only_fields = fields
