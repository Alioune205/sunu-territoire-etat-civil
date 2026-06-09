import re
import uuid

def process_ndiogoye_chat(message: str, conversation_id: str = None) -> dict:
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        
    message_lower = message.lower()
    
    intent = "inconnu"
    action = "none"
    reply = "Je n'ai pas bien compris. Pouvez-vous reformuler ou me préciser si vous souhaitez créer un dossier, suivre une demande, ou avoir des informations ?"

    # Intentions à gérer : creer_dossier · suivre_dossier · info_procedure · salutation · inconnu
    
    if re.search(r'\b(bonjour|salut|coucou|hello)\b', message_lower):
        intent = "salutation"
        reply = "Bonjour ! Je suis Ndiogoye, l'assistant IA de TERANGA CIVIL. Comment puis-je vous aider aujourd'hui ?"
        
    elif re.search(r'\b(créer|creer|nouveau|nouvelle|demande|obtenir|veux|voudrais|besoin)\b.*\b(dossier|acte|extrait|certificat|document)\b', message_lower) or \
         re.search(r'\b(acte.*naissance|extrait.*naissance)\b', message_lower):
        intent = "creer_dossier"
        action = "start_dossier"
        reply = "Bien sûr ! Je peux vous aider à créer un nouveau dossier. Quel type d'acte souhaitez-vous demander (naissance, mariage, décès) et pour quelle commune ?"
        
    elif re.search(r'\b(suivre|suivi|état|etat|statut|où en est|ou en est)\b.*\b(dossier|demande)\b', message_lower):
        intent = "suivre_dossier"
        action = "check_status"
        reply = "Pour suivre votre dossier, veuillez me fournir le numéro de référence de votre demande."
        
    elif re.search(r'\b(comment|procédure|procedure|étape|etape|pièce|piece|fournir|faut-il)\b', message_lower):
        intent = "info_procedure"
        reply = "Pour les informations de procédure : en général, vous aurez besoin de pièces d'identité et de documents spécifiques au type d'acte (comme un certificat médical pour une naissance). Avez-vous une demande spécifique en tête ?"
        
    return {
        "reply": reply,
        "action": action,
        "intent": intent,
        "conversation_id": conversation_id
    }
