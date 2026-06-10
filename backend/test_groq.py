import os
import django
import sys

# Setup Django
sys.path.append(r"c:\Users\HP\Documents\Institut_Supérieur_d'enseignement_professionnelle_(ISEP)\Hackathon\backend")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.ai.chatbot import chat_orchestrator
from django.contrib.auth import get_user_model

try:
    print('Testing Groq Chat Orchestrator...')
    User = get_user_model()
    # Mock user or None
    user = User.objects.first() if User.objects.exists() else None
    
    response = chat_orchestrator(user, "Bonjour, je veux suivre mon dossier")
    print('Response from Groq:')
    print(response)
    print('Success!')
except Exception as e:
    print('Error:', e)
