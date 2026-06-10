"""
URL configuration for the AI module.
"""
from django.urls import path
from .views import OcrExtractView, OcrCameraView, OcrConfirmView, FAQAssistantView, NdiogoyeChatView

urlpatterns = [
    # OCR — Upload de fichier (image/PDF)
    path('ocr/extract/', OcrExtractView.as_view(), name='ocr_extract'),
    # OCR — Capture caméra (image base64 depuis le navigateur)
    path('ocr/camera/', OcrCameraView.as_view(), name='ocr_camera'),
    # OCR — Confirmation des données extraites
    path('ocr/confirm/', OcrConfirmView.as_view(), name='ocr_confirm'),
    # FAQ Assistant
    path('faq/', FAQAssistantView.as_view(), name='faq_assistant'),
    # Ndiogoye Chat IA
    path('ndiogoye/chat/', NdiogoyeChatView.as_view(), name='ndiogoye_chat'),
]
