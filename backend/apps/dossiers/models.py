"""
Dossier and DossierComment models for administrative requests.
"""
from django.conf import settings
from django.db import models

from apps.shared.models import TimeStampedModel
from apps.shared.utils import generate_reference


class Dossier(TimeStampedModel):
    """
    Represents an administrative request (demande) made by a citizen.
    Follows the workflow: draft → submitted → in_review → approved/rejected → completed
    """

    class Type(models.TextChoices):
        BIRTH_CERTIFICATE = 'birth_certificate', 'Extrait de naissance'
        MARRIAGE_CERTIFICATE = 'marriage_certificate', 'Extrait de mariage'
        DEATH_CERTIFICATE = 'death_certificate', 'Certificat de décès'
        RESIDENCE_CERTIFICATE = 'residence_certificate', 'Certificat de résidence'
        OTHER = 'other', 'Autre'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Brouillon'
        SUBMITTED = 'submitted', 'Soumis'
        IN_REVIEW = 'in_review', 'En cours de vérification'
        APPROVED = 'approved', 'Approuvé'
        REJECTED = 'rejected', 'Rejeté'
        COMPLETED = 'completed', 'Terminé'

    reference = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='Référence',
        db_index=True,
    )
    type = models.CharField(
        max_length=30,
        choices=Type.choices,
        verbose_name='Type de dossier',
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='Statut',
        db_index=True,
    )
    citizen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dossiers',
        verbose_name='Citoyen',
    )
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_dossiers',
        verbose_name='Agent responsable',
    )
    commune = models.ForeignKey(
        'communes.Commune',
        on_delete=models.CASCADE,
        related_name='dossiers',
        verbose_name='Commune',
    )
    is_for_third_party = models.BooleanField(
        default=False,
        verbose_name='Pour une tierce personne',
    )
    third_party_cni = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='CNI de la tierce personne',
    )
    third_party_relation = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Lien de parenté',
    )
    notes = models.TextField(
        blank=True,
        default='',
        verbose_name='Notes',
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Métadonnées du registre',
    )
    rejection_reason = models.TextField(
        blank=True,
        default='',
        verbose_name='Motif de rejet',
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de soumission',
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de vérification',
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de complétion',
    )

    class Meta:
        verbose_name = 'Dossier'
        verbose_name_plural = 'Dossiers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['type']),
            models.Index(fields=['status']),
            models.Index(fields=['citizen']),
            models.Index(fields=['commune']),
            models.Index(fields=['status', 'commune']),
        ]

    def __str__(self):
        return f'{self.reference} — {self.get_type_display()} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_reference('DOS')
        super().save(*args, **kwargs)


class DossierComment(TimeStampedModel):
    """
    Comment on a dossier, from either the citizen or an agent.
    """
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Dossier',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dossier_comments',
        verbose_name='Auteur',
    )
    content = models.TextField(
        verbose_name='Contenu',
    )

    class Meta:
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['created_at']

    def __str__(self):
        return f'Commentaire de {self.author.full_name} sur {self.dossier.reference}'


class RegistreCivil(TimeStampedModel):
    """
    Simulates the National Civil Registry database.
    Used to verify if an act exists and matches the citizen's identity.
    """
    numero_registre = models.CharField(max_length=50, verbose_name='Numéro de registre')
    annee_registre = models.IntegerField(verbose_name='Année de registre')
    commune = models.ForeignKey(
        'communes.Commune',
        on_delete=models.CASCADE,
        related_name='registres',
        verbose_name='Commune de déclaration',
    )
    type_acte = models.CharField(
        max_length=30,
        choices=Dossier.Type.choices,
        verbose_name="Type d'acte",
    )
    nom_complet_personne = models.CharField(
        max_length=255,
        verbose_name='Nom complet sur le registre',
    )
    date_naissance_personne = models.DateField(
        verbose_name='Date de naissance sur le registre',
    )
    # Pour le mariage
    conjoint_nom_complet = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Nom complet du conjoint',
    )

    class Meta:
        verbose_name = 'Registre Civil (Simulation)'
        verbose_name_plural = 'Registres Civils (Simulation)'
        unique_together = ('numero_registre', 'annee_registre', 'commune', 'type_acte')
        ordering = ['-annee_registre', 'numero_registre']

    def __str__(self):
        return f'{self.numero_registre}/{self.annee_registre} - {self.nom_complet_personne} ({self.get_type_acte_display()})'
