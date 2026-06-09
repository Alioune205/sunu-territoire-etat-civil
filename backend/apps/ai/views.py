"""
AI module views for OCR, smart validation and FAQ assistance.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from .ocr import extract_text_from_image
from .validators import validate_citizen_document, check_dossier_duplicate
from .chatbot import chat_orchestrator

class OcrValidationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(tags=['AI & OCR'], summary="Extraire le texte d'un document et le valider")
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('document')
        dossier_type = request.data.get('dossier_type')

        if not file_obj:
            return Response({'error': 'Aucun document fourni.'}, status=400)

        # 1. Vérification des doublons (si le type de dossier est fourni)
        if dossier_type:
            duplicate_check = check_dossier_duplicate(request.user, dossier_type)
            if duplicate_check.get('is_duplicate'):
                return Response({
                    'error': 'Un dossier identique est déjà en cours de traitement.',
                    'details': duplicate_check
                }, status=400)

        # 2. Extraction du texte via OCR
        extracted_text = extract_text_from_image(file_obj)

        # 3. Validation Intelligente
        validation_result = None
        if hasattr(request.user, 'profile'):
            validation_result = validate_citizen_document(request.user.profile, extracted_text)

        return Response({
            'extracted_text': extracted_text,
            'validation': validation_result
        })

class FAQAssistantView(APIView):
    permission_classes = [IsAuthenticated]

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
