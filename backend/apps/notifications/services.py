"""
FCM Push Notification Service with integration safety fallbacks.
"""
import logging
from django.conf import settings
from .models import Notification, NotificationToken

logger = logging.getLogger('apps.notifications')


def send_fcm_notification(user, title, body, notification_type, data=None):
    """
    Sends a push notification to a user via FCM and records it in history.
    
    If firebase-admin is not installed or firebase is not configured,
    it falls back to logging the action and saving to the database history.
    """
    # 1. Save to database history
    notification = Notification.objects.create(
        user=user,
        title=title,
        body=body,
        type=notification_type,
        data=data or {}
    )

    # 2. Get active tokens for the user
    tokens = list(NotificationToken.objects.filter(user=user, is_active=True).values_list('token', flat=True))
    if not tokens:
        logger.info(
            f"Notification [ID: {notification.id}] enregistrée dans l'historique. "
            f"Aucun token FCM actif trouvé pour {user.email}."
        )
        return notification

    # 3. Attempt FCM send
    try:
        import firebase_admin
        from firebase_admin import messaging

        # Initialize Firebase if not already initialized
        try:
            firebase_admin.get_app()
        except ValueError:
            # Attempt to initialize firebase with settings configuration if available
            firebase_config = getattr(settings, 'FIREBASE_CREDENTIALS', None)
            if firebase_config:
                cred = firebase_admin.credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()

        # Build message payload
        messages = [
            messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={k: str(v) for k, v in (data or {}).items()},
                token=token,
            ) for token in tokens
        ]

        # Send messages
        response = messaging.send_each(messages)
        logger.info(
            f"FCM: Envoi réussi pour {response.success_count} appareils, "
            f"échec pour {response.failure_count} appareils."
        )
        
        # Cleanup invalid tokens (optional helper)
        if response.failure_count > 0:
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    # If token is invalid/expired, mark token as inactive
                    bad_token = tokens[idx]
                    NotificationToken.objects.filter(token=bad_token).update(is_active=False)
                    logger.info(f"Désactivation du token FCM invalide: {bad_token[:20]}...")

    except ImportError:
        logger.warning(
            f"[STUB MODE] Envoi de notification simulé pour {user.email}. "
            f"Titre: '{title}' | Corps: '{body}' | Tokens: {tokens}"
        )
    except Exception as e:
        logger.error(f"Erreur lors de la communication avec FCM : {str(e)}")

    return notification
