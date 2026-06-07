"""
URL configuration for the AI module.
"""
from django.urls import path
from .views import OcrValidationView, FAQAssistantView

urlpatterns = [
    path('ocr-validate/', OcrValidationView.as_view(), name='ocr_validate'),
    path('faq/', FAQAssistantView.as_view(), name='faq_assistant'),
]
