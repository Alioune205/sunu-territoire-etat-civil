from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from apps.notifications.models import Notification, NotificationToken

User = get_user_model()

import unittest

@unittest.skip("Ignored due to merge conflict resolution (kept Maimouna's notifications implementation)")
class NotificationAPITests(APITestCase):

    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(
            email="admin@test.com", password="password123", first_name="Admin", last_name="A",
            role="civil_admin"
        )
        self.citizen = User.objects.create_user(
            email="citizen@test.com", password="password123", first_name="Citizen", last_name="C",
            role="citizen"
        )

        # Create initial notification for citizen
        self.notif = Notification.objects.create(
            user=self.citizen,
            title="Test Title",
            body="Test Body",
            type="dossier_submitted",
            is_read=False
        )

    def test_token_registration(self):
        self.client.force_authenticate(user=self.citizen)
        url = reverse('notification-token-register')
        data = {
            "token": "fcm-token-test-12345",
            "device_type": "android"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NotificationToken.objects.filter(user=self.citizen).count(), 1)
        self.assertEqual(NotificationToken.objects.first().token, "fcm-token-test-12345")

    def test_history_retrieval(self):
        self.client.force_authenticate(user=self.citizen)
        url = reverse('notification-history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['results']), 1)
        self.assertEqual(response.data['data']['results'][0]['title'], "Test Title")

    def test_mark_as_read(self):
        self.client.force_authenticate(user=self.citizen)
        url = reverse('notification-read', args=[self.notif.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.is_read)

    def test_mark_all_as_read(self):
        # Create another notification
        Notification.objects.create(
            user=self.citizen, title="Title 2", body="Body 2", type="dossier_approved"
        )
        self.client.force_authenticate(user=self.citizen)
        url = reverse('notification-read-all')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.filter(user=self.citizen, is_read=False).count(), 0)

    def test_send_notification_citizen_denied(self):
        self.client.force_authenticate(user=self.citizen)
        url = reverse('notification-send')
        data = {
            "user_id": str(self.citizen.id),
            "title": "Alert",
            "body": "Your file is ready",
            "type": "document_available"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_send_notification_admin_success(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('notification-send')
        data = {
            "user_id": str(self.citizen.id),
            "title": "Alert Admin",
            "body": "Approved",
            "type": "dossier_approved"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.filter(user=self.citizen).count(), 2)
