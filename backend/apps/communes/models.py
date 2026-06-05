"""
Commune model for territorial collectivities.
"""
from django.db import models

from apps.shared.models import TimeStampedModel


class Commune(TimeStampedModel):
    """
    Represents a Senegalese commune (local government entity).
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Nom',
    )
    region = models.CharField(
        max_length=100,
        verbose_name='Région',
        db_index=True,
    )
    department = models.CharField(
        max_length=100,
        verbose_name='Département',
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Code administratif',
    )
    address = models.TextField(
        blank=True,
        default='',
        verbose_name='Adresse',
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Téléphone',
    )
    email = models.EmailField(
        blank=True,
        default='',
        verbose_name='Email',
    )

    class Meta:
        verbose_name = 'Commune'
        verbose_name_plural = 'Communes'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['region']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return f'{self.name} ({self.region})'
