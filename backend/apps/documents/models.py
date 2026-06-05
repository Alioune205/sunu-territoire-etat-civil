"""
Document model for file attachments on dossiers.
"""
from django.conf import settings
from django.db import models

from apps.shared.models import TimeStampedModel
from apps.shared.validators import validate_document_file


def document_upload_path(instance, filename):
    """Generate upload path: documents/<dossier_id>/<filename>"""
    return f'documents/{instance.dossier_id}/{filename}'


class Document(TimeStampedModel):
    """
    File attachment linked to a dossier.
    Supports OCR status tracking for future AI integration (DEV 2).
    """

    class FileType(models.TextChoices):
        PDF = 'pdf', 'PDF'
        IMAGE = 'image', 'Image'
        SCAN = 'scan', 'Scan'

    class OCRStatus(models.TextChoices):
        PENDING = 'pending', 'En attente'
        PROCESSING = 'processing', 'En cours'
        COMPLETED = 'completed', 'Terminé'
        FAILED = 'failed', 'Échoué'

    dossier = models.ForeignKey(
        'dossiers.Dossier',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Dossier',
    )
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[validate_document_file],
        verbose_name='Fichier',
    )
    original_filename = models.CharField(
        max_length=255,
        verbose_name='Nom original',
    )
    file_type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        verbose_name='Type de fichier',
    )
    file_size = models.IntegerField(
        verbose_name='Taille (bytes)',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Description',
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_documents',
        verbose_name='Téléversé par',
    )
    # OCR fields (for DEV 2 / AI team)
    ocr_status = models.CharField(
        max_length=15,
        choices=OCRStatus.choices,
        default=OCRStatus.PENDING,
        verbose_name='Statut OCR',
    )
    ocr_text = models.TextField(
        blank=True,
        default='',
        verbose_name='Texte OCR',
    )

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dossier']),
            models.Index(fields=['uploaded_by']),
            models.Index(fields=['ocr_status']),
        ]

    def __str__(self):
        return f'{self.original_filename} ({self.dossier.reference})'

    def save(self, *args, **kwargs):
        if self.file and not self.original_filename:
            self.original_filename = self.file.name
        if self.file and not self.file_size:
            self.file_size = self.file.size
        if self.file and not self.file_type:
            ext = self.file.name.rsplit('.', 1)[-1].lower()
            if ext == 'pdf':
                self.file_type = self.FileType.PDF
            elif ext in ('jpg', 'jpeg', 'png'):
                self.file_type = self.FileType.IMAGE
            else:
                self.file_type = self.FileType.SCAN
        super().save(*args, **kwargs)
