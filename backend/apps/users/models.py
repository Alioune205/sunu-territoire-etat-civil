"""
User and CitizenProfile models for TERANGA CIVIL.
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from ..shared.validators import validate_phone_senegal, validate_cni
from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email as the unique identifier.
    Supports RBAC via the `role` field.
    """

    class Role(models.TextChoices):
        CITIZEN = 'citizen', 'Citoyen'
        RECEPTION_AGENT = 'reception_agent', 'Agent de réception'
        VERIFICATION_AGENT = 'verification_agent', 'Agent de vérification'
        CIVIL_ADMIN = 'civil_admin', 'Administrateur d\'état civil'
        SUPER_ADMIN = 'super_admin', 'Super administrateur'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Adresse email',
    )
    phone = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        validators=[validate_phone_senegal],
        verbose_name='Téléphone',
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Prénom',
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Nom',
    )
    role = models.CharField(
        max_length=25,
        choices=Role.choices,
        default=Role.CITIZEN,
        verbose_name='Rôle',
        db_index=True,
    )
    commune = models.ForeignKey(
        'communes.Commune',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Commune',
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Vérifié',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Actif',
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Staff',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Date de modification',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['commune']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_admin_staff(self):
        """Check if user has any administrative role."""
        return self.role in [
            self.Role.RECEPTION_AGENT,
            self.Role.VERIFICATION_AGENT,
            self.Role.CIVIL_ADMIN,
            self.Role.SUPER_ADMIN,
        ]


class CitizenProfile(models.Model):
    """
    Extended profile for citizens with personal information.
    Auto-created when a citizen user is registered.
    """

    class Gender(models.TextChoices):
        MALE = 'M', 'Masculin'
        FEMALE = 'F', 'Féminin'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Utilisateur',
    )
    address = models.TextField(
        blank=True,
        default='',
        verbose_name='Adresse',
    )
    cni_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        validators=[validate_cni],
        verbose_name='Numéro CNI',
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date de naissance',
    )
    place_of_birth = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Lieu de naissance',
    )
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        blank=True,
        default='',
        verbose_name='Genre',
    )
    profession = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Profession',
    )
    photo = models.ImageField(
        upload_to='profiles/photos/',
        null=True,
        blank=True,
        verbose_name='Photo',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Date de modification',
    )

    class Meta:
        verbose_name = 'Profil citoyen'
        verbose_name_plural = 'Profils citoyens'

    def __str__(self):
        return f'Profil de {self.user.full_name}'
