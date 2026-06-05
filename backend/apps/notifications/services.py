import logging
from .models import Notification, FCMDevice
from django.conf import settings

logger = logging.getLogger('system')

class FCMService:
    """
    Mock service for sending Firebase Cloud Messaging notifications.
    In a real implementation, this would use the `firebase-admin` Python SDK.
    """
    @staticmethod
    def send_notification_to_user(user, title, body, notification_type=Notification.TypeChoices.INFO, data=None):
        """
        Creates a notification record and sends an FCM push to all active devices of the user.
        """
        # 1. Create the database record
        notification = Notification.objects.create(
            user=user,
            title=title,
            body=body,
            notification_type=notification_type,
            data=data
        )

        # 2. Get active devices
        devices = FCMDevice.objects.filter(user=user, is_active=True)
        if not devices.exists():
            logger.info(f"No active FCM devices found for user {user.id}")
            return notification

        tokens = list(devices.values_list('registration_id', flat=True))

        # 3. Mock FCM Send
        logger.info(f"[MOCK FCM] Sending push '{title}' to {len(tokens)} devices for user {user.id}.")
        # In real code:
        # message = messaging.MulticastMessage(
        #     notification=messaging.Notification(title=title, body=body),
        #     data=data or {},
        #     tokens=tokens,
        # )
        # response = messaging.send_multicast(message)

        return notification
