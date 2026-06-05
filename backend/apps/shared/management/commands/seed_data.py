import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.communes.models import Commune
from apps.dossiers.models import Dossier

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # 1. Create Communes
        communes_data = [
            {'name': 'Dakar Plateau', 'region': 'Dakar', 'department': 'Dakar', 'code': 'DK-PLT'},
            {'name': 'Médina', 'region': 'Dakar', 'department': 'Dakar', 'code': 'DK-MED'},
            {'name': 'Pikine', 'region': 'Dakar', 'department': 'Pikine', 'code': 'DK-PIK'},
            {'name': 'Rufisque', 'region': 'Dakar', 'department': 'Rufisque', 'code': 'DK-RUF'},
            {'name': 'Saint-Louis', 'region': 'Saint-Louis', 'department': 'Saint-Louis', 'code': 'SL-STL'},
            {'name': 'Thiès', 'region': 'Thiès', 'department': 'Thiès', 'code': 'TH-THI'},
        ]

        communes = []
        for c_data in communes_data:
            commune, created = Commune.objects.get_or_create(code=c_data['code'], defaults=c_data)
            communes.append(commune)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created commune: {commune.name}"))

        dakar_plateau = communes[0]

        # 2. Create Users
        users_data = [
            # Super Admin
            {'email': 'superadmin@sunucivil.sn', 'role': User.Role.SUPER_ADMIN, 'first_name': 'Super', 'last_name': 'Admin', 'is_staff': True, 'is_superuser': True, 'is_verified': True, 'commune': None},
            # Civil Admin
            {'email': 'admin.plateau@sunucivil.sn', 'role': User.Role.CIVIL_ADMIN, 'first_name': 'Maire', 'last_name': 'Plateau', 'is_staff': True, 'is_verified': True, 'commune': dakar_plateau},
            # Verification Agent
            {'email': 'verifier.plateau@sunucivil.sn', 'role': User.Role.VERIFICATION_AGENT, 'first_name': 'Agent', 'last_name': 'Verif', 'is_staff': True, 'is_verified': True, 'commune': dakar_plateau},
            # Reception Agent
            {'email': 'reception.plateau@sunucivil.sn', 'role': User.Role.RECEPTION_AGENT, 'first_name': 'Agent', 'last_name': 'Recept', 'is_staff': True, 'is_verified': True, 'commune': dakar_plateau},
            # Citizens
            {'email': 'citoyen1@gmail.com', 'role': User.Role.CITIZEN, 'first_name': 'Moussa', 'last_name': 'Diop', 'phone': '+221771234567', 'is_verified': True, 'commune': dakar_plateau},
            {'email': 'citoyen2@gmail.com', 'role': User.Role.CITIZEN, 'first_name': 'Awa', 'last_name': 'Fall', 'phone': '+221779876543', 'is_verified': True, 'commune': dakar_plateau},
        ]

        citizens = []
        agents = []

        for u_data in users_data:
            if not User.objects.filter(email=u_data['email']).exists():
                commune = u_data.pop('commune')
                is_staff = u_data.pop('is_staff', False)
                is_superuser = u_data.pop('is_superuser', False)

                if is_superuser:
                    user = User.objects.create_superuser(password='password123', **u_data)
                else:
                    user = User.objects.create_user(password='password123', **u_data)
                
                user.is_staff = is_staff
                user.commune = commune
                user.save()

                if user.role == User.Role.CITIZEN:
                    citizens.append(user)
                    # Update citizen profile
                    profile = user.profile
                    profile.cni_number = f"1{''.join([str(random.randint(0,9)) for _ in range(12)])}"
                    profile.address = f"Rue {random.randint(1, 100)}, {commune.name if commune else 'Dakar'}"
                    profile.save()
                else:
                    agents.append(user)

                self.stdout.write(self.style.SUCCESS(f"Created user: {user.email} ({user.role})"))

        # 3. Create Dossiers
        if citizens and dakar_plateau:
            dossiers_data = [
                {'citizen': citizens[0], 'commune': dakar_plateau, 'type': Dossier.Type.BIRTH_CERTIFICATE, 'status': Dossier.Status.COMPLETED, 'notes': 'Demande traitée rapidement.'},
                {'citizen': citizens[0], 'commune': dakar_plateau, 'type': Dossier.Type.RESIDENCE_CERTIFICATE, 'status': Dossier.Status.IN_REVIEW},
                {'citizen': citizens[1], 'commune': dakar_plateau, 'type': Dossier.Type.MARRIAGE_CERTIFICATE, 'status': Dossier.Status.SUBMITTED},
                {'citizen': citizens[1], 'commune': dakar_plateau, 'type': Dossier.Type.BIRTH_CERTIFICATE, 'status': Dossier.Status.DRAFT},
            ]

            verifier = next((a for a in agents if a.role == User.Role.VERIFICATION_AGENT), None)

            for d_data in dossiers_data:
                if not Dossier.objects.filter(citizen=d_data['citizen'], type=d_data['type']).exists():
                    dossier = Dossier.objects.create(**d_data)
                    if dossier.status == Dossier.Status.COMPLETED:
                        dossier.submitted_at = timezone.now()
                        dossier.reviewed_at = timezone.now()
                        dossier.completed_at = timezone.now()
                        dossier.assigned_agent = verifier
                    elif dossier.status == Dossier.Status.IN_REVIEW:
                        dossier.submitted_at = timezone.now()
                        dossier.reviewed_at = timezone.now()
                        dossier.assigned_agent = verifier
                    elif dossier.status == Dossier.Status.SUBMITTED:
                        dossier.submitted_at = timezone.now()
                    dossier.save()
                    self.stdout.write(self.style.SUCCESS(f"Created dossier: {dossier.reference} ({dossier.get_type_display()})"))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write(self.style.WARNING('All passwords are: password123'))
