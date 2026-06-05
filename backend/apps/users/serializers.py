"""
Serializers for User and CitizenProfile.
"""
from rest_framework import serializers

from .models import User, CitizenProfile


class CitizenProfileSerializer(serializers.ModelSerializer):
    """Serializer for CitizenProfile model."""

    class Meta:
        model = CitizenProfile
        fields = [
            'id',
            'address',
            'cni_number',
            'date_of_birth',
            'place_of_birth',
            'gender',
            'profession',
            'photo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for reading User data."""
    profile = CitizenProfileSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'phone',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'commune',
            'is_verified',
            'is_active',
            'profile',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'email', 'role', 'is_verified',
            'created_at', 'updated_at',
        ]


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for user lists (no nested profile)."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'phone',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'commune',
            'is_verified',
            'is_active',
            'created_at',
        ]
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating User data (limited fields)."""

    class Meta:
        model = User
        fields = [
            'phone',
            'first_name',
            'last_name',
            'commune',
        ]


class CitizenProfileDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for CitizenProfile with nested user info."""
    user = UserListSerializer(read_only=True)

    class Meta:
        model = CitizenProfile
        fields = [
            'id',
            'user',
            'address',
            'cni_number',
            'date_of_birth',
            'place_of_birth',
            'gender',
            'profession',
            'photo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
