"""
Views for QR Code generation and validation.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import extend_schema

from apps.dossiers.models import Dossier
from apps.shared.responses import success_response, error_response


@extend_schema(tags=['QR Code Public Verification'], summary='Vérifier l\'authenticité d\'un document')
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_document(request, reference):
    """
    GET /api/qr/verify/{reference}/
    Vérifie l'authenticité d'un document via sa référence (contenue dans le QR Code).
    """
    try:
        dossier = Dossier.objects.get(reference=reference, status=Dossier.Status.APPROVED)
        
        # Retourne des données publiques non sensibles
        public_data = {
            'reference': dossier.reference,
            'type': dossier.get_type_display(),
            'status': dossier.get_status_display(),
            'citizen_name': dossier.citizen.full_name,
            'commune': dossier.commune.name if dossier.commune else None,
            'completed_at': dossier.completed_at,
        }
        
        return success_response(
            data=public_data,
            message='Document authentique et valide.'
        )
    except Dossier.DoesNotExist:
        return error_response(
            message='Document introuvable, invalide ou non approuvé.',
            status_code=status.HTTP_404_NOT_FOUND
        )
