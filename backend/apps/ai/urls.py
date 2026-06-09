"""
URL configuration for the AI module.
"""
from django.urls import path
from .views import OcrExtractView, OcrConfirmView, FAQAssistantView, NdiogoyeChatView

urlpatterns = [
    path('ocr/extract/', OcrExtractView.as_view(), name='ocr_extract'),
    path('ocr/confirm/', OcrConfirmView.as_view(), name='ocr_confirm'),
    path('faq/', FAQAssistantView.as_view(), name='faq_assistant'),
    path('ndiogoye/chat/', NdiogoyeChatView.as_view(), name='ndiogoye_chat'),
]
