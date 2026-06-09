"""
AI module views for OCR, smart validation and FAQ assistance.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from .ocr import extract_text_from_image, extract_cni_data
from .validators import validate_citizen_document, check_dossier_duplicate
from .faq import get_faq_answer
from .ndiogoye import process_ndiogoye_chat

class OcrExtractView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(tags=['AI & OCR'], summary="Extraire les données d'un document via OCR")
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

        # 2. Extraction du texte et données structurées via OCR
        extracted_text = extract_text_from_image(file_obj)
        file_obj.seek(0)
        extracted_data = extract_cni_data(file_obj)

        # 3. Validation Intelligente
        validation_result = None
        if hasattr(request.user, 'profile'):
            validation_result = validate_citizen_document(request.user.profile, extracted_text)

        return Response({
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

        # L'utilisateur valide les données extraites
        # (Elles peuvent être sauvegardées ici si nécessaire)
        return Response({
            'message': 'Données confirmées avec succès.',
            'document_id': document_id,
            'confirmed_data': confirmed_data
        })

class FAQAssistantView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=['AI & OCR'], summary="Poser une question à l'assistant FAQ")
    def post(self, request, *args, **kwargs):
        question = request.data.get('question', '')
        
        if not question:
            return Response({'error': 'Veuillez poser une question.'}, status=400)
            
        answer = get_faq_answer(question)
        
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
