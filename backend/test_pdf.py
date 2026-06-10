import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.communes.models import Commune
from apps.dossiers.models import Dossier
from apps.dossiers.services.pdf_generator import generate_signed_certificate
from apps.documents.models import GeneratedCertificate

User = get_user_model()

# 1. Obtenir une commune (Dakar Plateau par exemple)
commune = Commune.objects.filter(code='DKR-PLT').first()
if not commune:
    print("Commune DKR-PLT non trouvée.")
    exit()

# 2. Obtenir ou créer un citoyen et un officier
citizen, _ = User.objects.get_or_create(
    email='citizen@test.com',
    defaults={'first_name': 'Lansana', 'last_name': 'Coly', 'role': 'citizen', 'phone': '+221770000001'}
)

officier, _ = User.objects.get_or_create(
    email='officier@test.com',
    defaults={'first_name': 'El Hadji Idrissa', 'last_name': 'Ndiaye', 'role': 'civil_admin', 'phone': '+221770000002'}
)

# 3. Créer un dossier fictif
dossier, created = Dossier.objects.get_or_create(
    reference='DOS-DEMO-PDF-1234',
    defaults={
        'citizen': citizen,
        'commune': commune,
        'type': 'birth_certificate',
        'status': 'in_review',
        'metadata': {
            'numero_registre': '2020-0142',
            'annee_registre': 2020,
            'prenoms_enfant': 'Lansana',
            'nom_enfant': 'Coly',
            'sexe': 'Masculin',
            'date_naissance_personne': '2000-05-15',
            'heure_naissance': '08:30',
            'lieu_naissance': 'Dakar',
            'prenom_pere': 'Ousmane',
            'prenom_mere': 'Fatou',
            'nom_mere': 'Ndiaye',
            'est_jugement_suppletif': True,
            'tribunal_competent': 'Tribunal d\'Instance de Dakar',
            'numero_jugement': 'JUG-2020-890',
            'date_jugement': '2020-06-10',
            'date_inscription': '2020-06-15',
            'annee_inscription': 2020,
        }
    }
)

# 4. Générer le certificat
try:
    # On supprime s'il existait déjà pour pouvoir le regénérer
    GeneratedCertificate.objects.filter(dossier=dossier).delete()
    
    cert = generate_signed_certificate(dossier, officier)
    print("==================================================")
    print("SUCCES : PDF Genere !")
    print(f"Emplacement du fichier : {cert.pdf_file.path}")
    print(f"🔒 Signature HMAC : {cert.hmac_signature}")
    print("==================================================")
except Exception as e:
    print(f"Erreur lors de la génération : {e}")
