import logging
from typing import Dict, Optional
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError

from django.contrib.auth import get_user_model
from .models import DeviceToken

logger = logging.getLogger('system')
User = get_user_model()


def send_push_notification(user: User, title: str, body: str, data: Optional[Dict[str, str]] = None) -> None:
    """
    Envoie une notification push Firebase à tous les appareils enregistrés d'un utilisateur.
    
    Args:
        user (User): L'utilisateur cible.
        title (str): Titre de la notification.
        body (str): Contenu de la notification.
        data (dict, optional): Payload de données supplémentaires.
    """
    tokens = list(DeviceToken.objects.filter(user=user).values_list('token', flat=True))
    
    if not tokens:
        logger.info(f"Aucun token FCM trouvé pour l'utilisateur {user.id}")
        return

    messages = [
        messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            token=token
        ) for token in tokens
    ]

    try:
        response: messaging.BatchResponse = messaging.send_each(messages)
        
        logger.info(f"FCM: {response.success_count} notifications envoyées à {user.id}")
        
        if response.failure_count > 0:
            logger.warning(f"FCM: {response.failure_count} échecs pour l'utilisateur {user.id}")
            
    except FirebaseError as e:
        logger.error(f"Erreur Firebase critique pour l'utilisateur {user.id}: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'envoi FCM (User: {user.id}): {str(e)}", exc_info=True)
