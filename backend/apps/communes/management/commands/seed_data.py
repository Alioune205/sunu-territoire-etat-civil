"""
Management command to seed the database with communes, registre civil data,
and test users for the hackathon demo.
"""
from django.core.management.base import BaseCommand
from apps.communes.models import Commune
from apps.dossiers.models import RegistreCivil


COMMUNES_DATA = [
    {
        'name': 'Dakar Plateau',
        'region': 'Dakar',
        'department': 'Dakar',
        'code': 'DKR-PLT',
        'address': 'Place de l\'Indépendance, Dakar Plateau',
        'phone': '+221 33 821 00 00',
        'email': 'mairie@dakarplateau.sn',
    },
    {
        'name': 'Keur Massar',
        'region': 'Dakar',
        'department': 'Keur Massar',
        'code': 'DKR-KMS',
        'address': 'Avenue principale, Keur Massar',
        'phone': '+221 33 879 00 00',
        'email': 'mairie@keurmassar.sn',
    },
    {
        'name': 'Ndiaganiao',
        'region': 'Thiès',
        'department': 'Mbour',
        'code': 'THS-NDG',
        'address': 'Centre-ville, Ndiaganiao',
        'phone': '+221 33 957 00 00',
        'email': 'mairie@ndiaganiao.sn',
    },
]

# Données fictives du registre civil pour la démo
REGISTRE_DATA = [
    # === Dakar Plateau ===
    {
        'numero_registre': '2020-0142',
        'annee_registre': 2020,
        'commune_code': 'DKR-PLT',
        'type_acte': 'birth_certificate',
        'nom_complet_personne': 'Lansana Coly',
        'date_naissance_personne': '2000-05-15',
    },
    {
        'numero_registre': '2019-0301',
        'annee_registre': 2019,
        'commune_code': 'DKR-PLT',
        'type_acte': 'birth_certificate',
        'nom_complet_personne': 'Aminata Diallo',
        'date_naissance_personne': '1995-03-22',
    },
    {
        'numero_registre': '2021-0089',
        'annee_registre': 2021,
        'commune_code': 'DKR-PLT',
        'type_acte': 'marriage_certificate',
        'nom_complet_personne': 'Moussa Ndiaye',
        'date_naissance_personne': '1988-11-10',
        'conjoint': 'Fatou Sow',
    },
    {
        'numero_registre': '2023-0015',
        'annee_registre': 2023,
        'commune_code': 'DKR-PLT',
        'type_acte': 'death_certificate',
        'nom_complet_personne': 'Ibrahima Fall',
        'date_naissance_personne': '1950-01-01',
    },
    # === Keur Massar ===
    {
        'numero_registre': '2022-0567',
        'annee_registre': 2022,
        'commune_code': 'DKR-KMS',
        'type_acte': 'birth_certificate',
        'nom_complet_personne': 'Ousmane Ba',
        'date_naissance_personne': '2002-08-30',
    },
    {
        'numero_registre': '2018-0233',
        'annee_registre': 2018,
        'commune_code': 'DKR-KMS',
        'type_acte': 'birth_certificate',
        'nom_complet_personne': 'Aissatou Diop',
        'date_naissance_personne': '1998-12-05',
    },
    {
        'numero_registre': '2020-0078',
        'annee_registre': 2020,
        'commune_code': 'DKR-KMS',
        'type_acte': 'marriage_certificate',
        'nom_complet_personne': 'Abdoulaye Sarr',
        'date_naissance_personne': '1990-06-18',
        'conjoint': 'Marième Gueye',
    },
    # === Ndiaganiao ===
    {
        'numero_registre': '2021-0045',
        'annee_registre': 2021,
        'commune_code': 'THS-NDG',
        'type_acte': 'birth_certificate',
        'nom_complet_personne': 'Modou Faye',
        'date_naissance_personne': '2001-04-12',
    },
    {
        'numero_registre': '2019-0112',
        'annee_registre': 2019,
        'commune_code': 'THS-NDG',
        'type_acte': 'birth_certificate',
        'nom_complet_personne': 'Ndèye Mbaye',
        'date_naissance_personne': '1997-09-25',
    },
    {
        'numero_registre': '2023-0008',
        'annee_registre': 2023,
        'commune_code': 'THS-NDG',
        'type_acte': 'death_certificate',
        'nom_complet_personne': 'Cheikh Dieng',
        'date_naissance_personne': '1945-02-14',
    },
]


class Command(BaseCommand):
    help = 'Seed the database with communes and registre civil data for hackathon demo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('=== Seeding des Communes ==='))

        for data in COMMUNES_DATA:
            commune, created = Commune.objects.update_or_create(
                code=data['code'],
                defaults=data,
            )
            status = 'CRÉÉE' if created else 'MÀJ'
            self.stdout.write(f'  [{status}] {commune.name} ({commune.code})')

        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('=== Seeding du Registre Civil ==='))

        for entry in REGISTRE_DATA:
            commune = Commune.objects.get(code=entry['commune_code'])
            registre, created = RegistreCivil.objects.update_or_create(
                numero_registre=entry['numero_registre'],
                annee_registre=entry['annee_registre'],
                commune=commune,
                type_acte=entry['type_acte'],
                defaults={
                    'nom_complet_personne': entry['nom_complet_personne'],
                    'date_naissance_personne': entry['date_naissance_personne'],
                    'conjoint_nom_complet': entry.get('conjoint'),
                },
            )
            status = 'CRÉÉ' if created else 'MÀJ'
            self.stdout.write(
                f'  [{status}] {registre.numero_registre}/{registre.annee_registre} '
                f'— {registre.nom_complet_personne} ({registre.get_type_acte_display()})'
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'✅ {Commune.objects.count()} communes, '
            f'{RegistreCivil.objects.count()} registres civils en base.'
        ))
