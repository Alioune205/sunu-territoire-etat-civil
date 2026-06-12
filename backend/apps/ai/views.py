"""
AI module views for OCR, smart validation and FAQ assistance.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from .ocr import (
    extract_text_from_image,
    extract_cni_data,
    extract_text_from_base64,
    extract_cni_data_from_base64,
)
from .validators import validate_citizen_document, check_dossier_duplicate
from .faq import find_closest_faq
from .ndiogoye import process_ndiogoye_chat


class OcrExtractView(APIView):
    """
    Endpoint OCR qui accepte deux modes :
    
    MODE 1 — Upload de fichier (multipart/form-data) :
        POST /api/ai/ocr/extract/
        Body : { "document": <fichier>, "dossier_type": "..." }
    
    MODE 2 — Image caméra en base64 (application/json) :
        POST /api/ai/ocr/extract/
        Body : { "image_base64": "data:image/jpeg;base64,...", "dossier_type": "..." }
    """
    permission_classes = [IsAuthenticated]
    # Accepte multipart (upload fichier) ET JSON (base64 caméra)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @extend_schema(tags=['AI & OCR'], summary="Extraire les données d'un document via OCR (upload ou caméra)")
    def post(self, request, *args, **kwargs):
        dossier_type = request.data.get('dossier_type')
        image_base64 = request.data.get('image_base64')
        file_obj = request.FILES.get('document')

        # ── Vérification : au moins une source d'image est requise ──
        if not file_obj and not image_base64:
            return Response({
                'error': 'Aucun document fourni.',
                'hint': 'Envoyez "document" (fichier) ou "image_base64" (caméra).'
            }, status=400)

        # ── Vérification des doublons ──
        if dossier_type:
            duplicate_check = check_dossier_duplicate(request.user, dossier_type)
            if duplicate_check.get('is_duplicate'):
                return Response({
                    'error': 'Un dossier identique est déjà en cours de traitement.',
                    'details': duplicate_check
                }, status=400)

        # ── Extraction selon le mode ──
        if image_base64:
            # MODE 2 : Image capturée par la caméra du frontend (base64)
            source = 'camera'
            extracted_text = extract_text_from_base64(image_base64)
            extracted_data = extract_cni_data_from_base64(image_base64)
        else:
            # MODE 1 : Fichier uploadé (image ou PDF)
            source = 'upload'
            extracted_text = extract_text_from_image(file_obj)
            file_obj.seek(0)
            extracted_data = extract_cni_data(file_obj)

        # ── Validation intelligente ──
        validation_result = None
        if hasattr(request.user, 'profile'):
            validation_result = validate_citizen_document(request.user.profile, extracted_text)

        return Response({
            'source': source,
            'extracted_text': extracted_text,
            'extracted_data': extracted_data,
            'validation': validation_result
        })


class OcrCameraView(APIView):
    """
    Endpoint dédié à la capture caméra (WebRTC).
    Reçoit une image base64 et retourne les données CNI extraites.

    POST /api/ai/ocr/camera/
    Body (JSON) : {
        "image_base64": "data:image/jpeg;base64,/9j/...",
        "dossier_type": "naissance"   (optionnel)
    }
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser,)

    @extend_schema(tags=['AI & OCR'], summary="Extraire les données d'une capture caméra (base64)")
    def post(self, request, *args, **kwargs):
        image_base64 = request.data.get('image_base64')

        if not image_base64:
            return Response({
                'error': 'image_base64 est requis.',
                'hint': 'Envoyez l\'image capturée par la caméra en base64 (data URI ou raw base64).'
            }, status=400)

        extracted_text = extract_text_from_base64(image_base64)
        extracted_data = extract_cni_data_from_base64(image_base64)

        # Validation intelligente si profil utilisateur disponible
        validation_result = None
        if hasattr(request.user, 'profile'):
            validation_result = validate_citizen_document(request.user.profile, extracted_text)

        return Response({
            'source': 'camera',
            'extracted_text': extracted_text,
            'extracted_data': extracted_data,
            'validation': validation_result
        })


class OcrConfirmView(APIView):
    """
    Endpoint de confirmation OCR.
    
    ATTENTION (Périmètre DEV 1D / Frontend) :
    Cet endpoint NE SAUVEGARDE PAS les données dans la base de données.
    L'enregistrement des informations structurées (Nom, Prénom, CNI) relève 
    du périmètre Core/Auth (DEV 1A) et Dossier. 
    
    Le flux attendu est le suivant :
    1. Frontend appelle `/api/ai/ocr/extract/` -> Reçoit les données JSON.
    2. Frontend pré-remplit ses formulaires. L'utilisateur vérifie et corrige.
    3. Frontend (Optionnel) appelle cet endpoint `/api/ai/ocr/confirm/` pour 
       valider formellement les données côté client (tracking/analytics).
    4. Frontend soumet la donnée finale à l'endpoint de création de dossier 
       (`/api/dossiers/`) ou d'inscription (`/api/auth/register/`).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['AI & OCR'], summary="Confirmer les données extraites d'un document (Validation Client)")
    def post(self, request, *args, **kwargs):
        document_id = request.data.get('document_id')
        confirmed_data = request.data.get('confirmed_data')

        if not confirmed_data:
            return Response({'error': 'confirmed_data est requis.'}, status=400)

        # Si un document existe déjà en base, on met à jour son statut OCR.
        if document_id:
            from apps.documents.models import Document
            try:
                doc = Document.objects.get(id=document_id, uploaded_by=request.user)
                doc.ocr_status = Document.OCRStatus.COMPLETED
                doc.ocr_text = str(confirmed_data)
                doc.save(update_fields=['ocr_status', 'ocr_text'])
            except Document.DoesNotExist:
                pass # Échec silencieux, le document n'a peut-être pas encore été créé

        return Response({
            'message': 'Données OCR confirmées. Veuillez procéder à la soumission finale via le module approprié (Dossier ou Profil).',
            'document_id': document_id,
            'confirmed_data': confirmed_data,
            'next_step': 'Soumettre ces données à /api/dossiers/ ou /api/auth/register/ selon le cas d\'usage.'
        })


class FAQAssistantView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=['AI & OCR'], summary="Poser une question à l'assistant FAQ")
    def post(self, request, *args, **kwargs):
        question = request.data.get('question', '')
        
        if not question:
            return Response({'error': 'Veuillez poser une question.'}, status=400)
            
        answer = find_closest_faq(question)
        
        return Response({
            'question': question,
            'answer': answer
        })


class NdiogoyeChatView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=['AI & OCR'], summary="Discuter avec l'assistant IA Ndiogoye")
    def post(self, request, *args, **kwargs):
        message = request.data.get('message', '')
        conversation_id = request.data.get('conversation_id')

        if not message:
            return Response({'error': 'Veuillez envoyer un message.'}, status=400)

        result = process_ndiogoye_chat(message, conversation_id)
        
        return Response(result)
