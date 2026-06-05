"""
Notifications services — Service FCM avec gestion d'erreurs robuste.

Architecture :
    - Création d'un enregistrement Notification en base
    - Envoi push FCM à tous les appareils actifs de l'utilisateur
    - Gestion des tokens invalides (désactivation automatique)
    - Logging structuré pour le monitoring
"""
import logging
from django.db import transaction
from .models import Notification, FCMDevice

logger = logging.getLogger('system')


class FCMService:
    """
    Service d'envoi de notifications push via Firebase Cloud Messaging.

    En production, remplacer les appels mock par le SDK `firebase-admin` :
        pip install firebase-admin
        import firebase_admin
        from firebase_admin import messaging

    L'architecture est prête pour le swap — seule la méthode `_send_to_devices`
    doit être modifiée.
    """

    @staticmethod
    def send_notification_to_user(user, title, body, notification_type=Notification.TypeChoices.INFO, data=None):
        """
        Crée une notification en base et envoie un push FCM.

        Args:
            user: L'utilisateur destinataire.
            title: Titre de la notification.
            body: Corps du message.
            notification_type: Type (INFO, ACTION, SUCCESS, ALERT).
            data: Données additionnelles pour le deep linking dans l'app mobile.

        Returns:
            Notification: L'objet notification créé, ou None en cas d'erreur.
        """
        try:
            # 1. Créer l'enregistrement en base (transaction atomique)
            with transaction.atomic():
                notification = Notification.objects.create(
                    user=user,
                    title=title,
                    body=body,
                    notification_type=notification_type,
                    data=data,
                )

            # 2. Récupérer les appareils actifs
            devices = FCMDevice.objects.filter(user=user, is_active=True)
            if not devices.exists():
                logger.info(
                    f'[FCM] Aucun appareil actif pour l\'utilisateur {user.id}. '
                    f'Notification #{notification.id} sauvegardée en base uniquement.'
                )
                return notification

            tokens = list(devices.values_list('registration_id', flat=True))

            # 3. Envoi push (mock en développement)
            FCMService._send_to_devices(tokens, title, body, data)

            logger.info(
                f'[FCM] Push envoyé — "{title}" → {len(tokens)} appareil(s) '
                f'pour l\'utilisateur {user.id}.'
            )

            return notification

        except Exception as e:
            logger.error(
                f'[FCM] Erreur lors de l\'envoi de notification à l\'utilisateur '
                f'{user.id} : {str(e)}',
                exc_info=True,
            )
            return None

    @staticmethod
    def _send_to_devices(tokens, title, body, data=None):
        """
        Envoi effectif aux appareils via FCM.

        En production, remplacer ce mock par :
            message = messaging.MulticastMessage(
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in (data or {}).items()},
                tokens=tokens,
            )
            response = messaging.send_each_for_multicast(message)

            # Désactiver les tokens invalides
            for idx, send_response in enumerate(response.responses):
                if send_response.exception:
                    FCMDevice.objects.filter(
                        registration_id=tokens[idx]
                    ).update(is_active=False)
        """
        logger.info(
            f'[MOCK FCM] Envoi simulé de "{title}" à {len(tokens)} appareil(s). '
            f'Data: {data}'
        )

    @staticmethod
    def send_bulk_notification(users, title, body, notification_type=Notification.TypeChoices.INFO, data=None):
        """
        Envoie une notification à plusieurs utilisateurs en une seule opération.
        Optimisé avec bulk_create pour réduire les requêtes DB.

        Args:
            users: QuerySet ou liste d'utilisateurs.
            title: Titre de la notification.
            body: Corps du message.
            notification_type: Type de notification.
            data: Données additionnelles.

        Returns:
            int: Nombre de notifications créées.
        """
        notifications = [
            Notification(
                user=user,
                title=title,
                body=body,
                notification_type=notification_type,
                data=data,
            )
            for user in users
        ]

        with transaction.atomic():
            created = Notification.objects.bulk_create(notifications)

        # Récupérer tous les tokens actifs en une seule requête
        user_ids = [u.id for u in users]
        tokens = list(
            FCMDevice.objects.filter(
                user_id__in=user_ids,
                is_active=True,
            ).values_list('registration_id', flat=True)
        )

        if tokens:
            FCMService._send_to_devices(tokens, title, body, data)

        logger.info(
            f'[FCM Bulk] {len(created)} notification(s) créée(s), '
            f'{len(tokens)} appareil(s) notifié(s).'
        )
        return len(created)
