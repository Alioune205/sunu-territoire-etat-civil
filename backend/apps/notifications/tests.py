"""
Notifications tests — Tests unitaires pour les notifications.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.communes.models import Commune
from apps.dossiers.models import Dossier
from .models import FCMDevice, Notification
from .services import FCMService
from .tasks import (
    send_stale_dossier_alerts,
    cleanup_old_notifications,
    notify_citizen_dossier_reminder,
)

User = get_user_model()


class NotificationModelTestCase(TestCase):
    """Tests pour les modèles Notification et FCMDevice."""

    def setUp(self):
        self.commune = Commune.objects.create(
            name='Dakar Plateau', region='Dakar', department='Dakar', code='DK001'
        )
        self.user = User.objects.create_user(
            email='citoyen@test.sn',
            password='testpass123',
            first_name='Amadou',
            last_name='Diop',
            role='citizen',
            commune=self.commune,
        )

    def test_create_notification(self):
        """Vérifier la création d'une notification."""
        notif = Notification.objects.create(
            user=self.user,
            title='Test notification',
            body='Corps du message test.',
            notification_type=Notification.TypeChoices.INFO,
        )
        self.assertIsNotNone(notif.id)
        self.assertFalse(notif.is_read)
        self.assertEqual(notif.notification_type, 'INFO')

    def test_create_fcm_device(self):
        """Vérifier l'enregistrement d'un appareil FCM."""
        device = FCMDevice.objects.create(
            user=self.user,
            registration_id='fake-token-12345',
            device_id='device-abc',
        )
        self.assertIsNotNone(device.id)
        self.assertTrue(device.is_active)

    def test_notification_ordering(self):
        """Vérifier que les notifications sont ordonnées par date décroissante."""
        Notification.objects.create(user=self.user, title='Ancien', body='...')
        Notification.objects.create(user=self.user, title='Récent', body='...')
        notifications = Notification.objects.filter(user=self.user)
        self.assertEqual(notifications.first().title, 'Récent')


class FCMServiceTestCase(TestCase):
    """Tests pour le service d'envoi FCM."""

    def setUp(self):
        self.commune = Commune.objects.create(
            name='Thiès', region='Thiès', department='Thiès', code='TH001'
        )
        self.user = User.objects.create_user(
            email='agent@test.sn',
            password='testpass123',
            first_name='Moussa',
            last_name='Fall',
            role='reception_agent',
            commune=self.commune,
        )

    def test_send_notification_creates_record(self):
        """Vérifier que send_notification_to_user crée un enregistrement en base."""
        notif = FCMService.send_notification_to_user(
            user=self.user,
            title='Test push',
            body='Message de test.',
            notification_type=Notification.TypeChoices.SUCCESS,
            data={'test_key': 'test_value'},
        )
        self.assertIsNotNone(notif)
        self.assertEqual(notif.title, 'Test push')
        self.assertEqual(notif.notification_type, 'SUCCESS')
        self.assertEqual(notif.data, {'test_key': 'test_value'})

    def test_send_notification_without_devices(self):
        """Vérifier que l'envoi fonctionne même sans appareils enregistrés."""
        notif = FCMService.send_notification_to_user(
            user=self.user,
            title='No device',
            body='Pas d\'appareil enregistré.',
        )
        self.assertIsNotNone(notif)
        self.assertEqual(Notification.objects.count(), 1)


class NotificationAPITestCase(TestCase):
    """Tests pour les endpoints API des notifications."""

    def setUp(self):
        self.client = APIClient()
        self.commune = Commune.objects.create(
            name='Saint-Louis', region='Saint-Louis', department='Saint-Louis', code='SL001'
        )
        self.user = User.objects.create_user(
            email='user@test.sn',
            password='testpass123',
            first_name='Fatou',
            last_name='Ndiaye',
            role='citizen',
            commune=self.commune,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_notifications(self):
        """Vérifier l'endpoint GET /api/notifications/."""
        Notification.objects.create(user=self.user, title='Notif 1', body='Body 1')
        Notification.objects.create(user=self.user, title='Notif 2', body='Body 2')

        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_mark_as_read(self):
        """Vérifier l'endpoint POST /api/notifications/{id}/mark_as_read/."""
        notif = Notification.objects.create(user=self.user, title='À lire', body='...')

        response = self.client.post(f'/api/notifications/{notif.id}/mark_as_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_mark_all_read(self):
        """Vérifier l'endpoint POST /api/notifications/mark_all_read/."""
        Notification.objects.create(user=self.user, title='N1', body='...')
        Notification.objects.create(user=self.user, title='N2', body='...')

        response = self.client.post('/api/notifications/mark_all_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        unread = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread, 0)

    def test_register_device(self):
        """Vérifier l'endpoint POST /api/notifications/devices/."""
        response = self.client.post('/api/notifications/devices/', {
            'registration_id': 'fcm-token-xyz-123',
            'device_id': 'samsung-galaxy-s23',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FCMDevice.objects.filter(registration_id='fcm-token-xyz-123').exists())

    def test_notifications_isolation(self):
        """Vérifier qu'un utilisateur ne voit pas les notifications d'un autre."""
        other_user = User.objects.create_user(
            email='other@test.sn',
            password='testpass123',
            first_name='Ibrahima',
            last_name='Sow',
            role='citizen',
            commune=self.commune,
        )
        Notification.objects.create(user=other_user, title='Autre', body='Private')

        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


class NotificationTasksTestCase(TestCase):
    """Tests pour les tâches automatisées de notifications."""

    def setUp(self):
        self.commune = Commune.objects.create(
            name='Ziguinchor', region='Ziguinchor', department='Ziguinchor', code='ZG001'
        )
        self.citizen = User.objects.create_user(
            email='citizen-task@test.sn',
            password='testpass123',
            first_name='Omar',
            last_name='Ba',
            role='citizen',
            commune=self.commune,
        )
        self.agent = User.objects.create_user(
            email='agent-task@test.sn',
            password='testpass123',
            first_name='Awa',
            last_name='Diallo',
            role='reception_agent',
            commune=self.commune,
        )

    def test_cleanup_old_notifications(self):
        """Vérifier la suppression des vieilles notifications lues."""
        from django.utils import timezone
        from datetime import timedelta

        old_notif = Notification.objects.create(
            user=self.citizen, title='Old', body='...', is_read=True,
        )
        # Force created_at to 100 days ago
        Notification.objects.filter(id=old_notif.id).update(
            created_at=timezone.now() - timedelta(days=100)
        )

        new_notif = Notification.objects.create(
            user=self.citizen, title='New', body='...', is_read=True,
        )

        deleted = cleanup_old_notifications(days=90)
        self.assertEqual(deleted, 1)
        self.assertTrue(Notification.objects.filter(id=new_notif.id).exists())
        self.assertFalse(Notification.objects.filter(id=old_notif.id).exists())
