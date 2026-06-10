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
from .chatbot import chat_orchestrator
from .faq import get_faq_answer
from .ndiogoye import process_ndiogoye_chat
from .models import NdiogoyeChatLog
from .serializers import NdiogoyeChatLogSerializer
from rest_framework import generics
from apps.shared.permissions import IsAdminStaff


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
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['AI & OCR'], summary="Confirmer les données extraites d'un document")
    def post(self, request, *args, **kwargs):
        document_id = request.data.get('document_id')
        confirmed_data = request.data.get('confirmed_data')

        if not confirmed_data:
            return Response({'error': 'confirmed_data est requis.'}, status=400)

        return Response({
            'message': 'Données confirmées avec succès.',
            'document_id': document_id,
            'confirmed_data': confirmed_data
        })


class FAQAssistantView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=['AI & OCR'], summary="Poser une question à l'assistant IA (RAG+)")
    def post(self, request, *args, **kwargs):
        question = request.data.get('question', '')
        chat_history = request.data.get('chat_history', [])
        
        if not question:
            return Response({'error': 'Veuillez poser une question.'}, status=400)
            
        answer = chat_orchestrator(
            user=request.user,
            user_message=question,
            chat_history=chat_history
        )
        
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
        
        # Sauvegarde en base de données
        NdiogoyeChatLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=result.get('conversation_id'),
            message=message,
            reply=result.get('reply'),
            intent=result.get('intent'),
            action=result.get('action')
        )
        
        return Response(result)

class NdiogoyeLogListView(generics.ListAPIView):
    """
    GET /api/ai/ndiogoye/logs/
    Liste paginée de l'historique des conversations avec le chatbot (Admin/Agent uniquement).
    """
    queryset = NdiogoyeChatLog.objects.select_related('user').all()
    serializer_class = NdiogoyeChatLogSerializer
    permission_classes = [IsAuthenticated, IsAdminStaff]
