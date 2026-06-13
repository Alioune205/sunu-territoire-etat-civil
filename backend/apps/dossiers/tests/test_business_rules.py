"""
Tests for Ibrahima's business rules.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from datetime import date

from apps.communes.models import Commune
from apps.dossiers.models import RegistreCivil, Dossier
from apps.users.models import CitizenProfile

from django.test import override_settings

User = get_user_model()

@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class BusinessRulesTests(APITestCase):
    def setUp(self):
        self.commune = Commune.objects.create(
            code="DKR-PLT",
            name="Plateau",
            department="Dakar",
            region="Dakar"
        )
        
        self.citizen = User.objects.create_user(
            email='citizen@example.com',
            password='password123',
            first_name='Alioune',
            last_name='Sene',
            role='citizen'
        )
        profile1 = self.citizen.profile
        profile1.cni_number = '1234567890123'
        profile1.save()
        
        self.citizen_no_cni = User.objects.create_user(
            email='citizen2@example.com',
            password='password123',
            first_name='Moussa',
            last_name='Diop',
            role='citizen'
        )
        profile2 = self.citizen_no_cni.profile
        profile2.cni_number = ''
        profile2.save()

        self.registre_alioune = RegistreCivil.objects.create(
            numero_registre='100',
            annee_registre=1990,
            commune=self.commune,
            type_acte=Dossier.Type.BIRTH_CERTIFICATE,
            prenoms_enfant='Alioune',
            nom_enfant='Sene',
            date_naissance_personne=date(1990, 1, 1),
            lieu_naissance='Dakar'
        )
        
        self.registre_other = RegistreCivil.objects.create(
            numero_registre='101',
            annee_registre=1995,
            commune=self.commune,
            type_acte=Dossier.Type.BIRTH_CERTIFICATE,
            prenoms_enfant='Fatou',
            nom_enfant='Ndiaye',
            date_naissance_personne=date(1995, 2, 2),
            lieu_naissance='Thies'
        )

        self.url = '/api/dossiers/verify-registry/'

    def test_verify_registry_success_self(self):
        """Rule: Citizen asking for their own act, names match."""
        self.client.force_authenticate(user=self.citizen)
        data = {
            'numero_registre': '100',
            'annee_registre': 1990,
            'commune': self.commune.id,
            'type_acte': Dossier.Type.BIRTH_CERTIFICATE,
            'is_for_third_party': False
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Acte trouvé', response.data['message'])

    def test_verify_registry_fail_self_wrong_name(self):
        """Rule: Citizen asking for their own act, but name in registry doesn't match."""
        self.client.force_authenticate(user=self.citizen)
        data = {
            'numero_registre': '101',
            'annee_registre': 1995,
            'commune': self.commune.id,
            'type_acte': Dossier.Type.BIRTH_CERTIFICATE,
            'is_for_third_party': False
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Les noms sur cet acte ne correspondent pas', response.data['message'])

    def test_verify_registry_success_third_party(self):
        """Rule: Citizen with CNI asking for a third party (Fatou's act)."""
        self.client.force_authenticate(user=self.citizen)
        data = {
            'numero_registre': '101',
            'annee_registre': 1995,
            'commune': self.commune.id,
            'type_acte': Dossier.Type.BIRTH_CERTIFICATE,
            'is_for_third_party': True
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_registry_fail_third_party_no_cni(self):
        """Rule: Citizen without CNI cannot ask for a third party."""
        self.client.force_authenticate(user=self.citizen_no_cni)
        data = {
            'numero_registre': '101',
            'annee_registre': 1995,
            'commune': self.commune.id,
            'type_acte': Dossier.Type.BIRTH_CERTIFICATE,
            'is_for_third_party': True
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('doit contenir un numéro de CNI valide', response.data['message'])

    def test_verify_registry_not_found(self):
        """Rule: Act not found in registry."""
        self.client.force_authenticate(user=self.citizen)
        data = {
            'numero_registre': '999',
            'annee_registre': 2000,
            'commune': self.commune.id,
            'type_acte': Dossier.Type.BIRTH_CERTIFICATE,
            'is_for_third_party': False
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
