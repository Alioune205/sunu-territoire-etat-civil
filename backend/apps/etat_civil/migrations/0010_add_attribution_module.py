from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dossiers', '0001_initial'), # Dépendance hypothétique pour Dossier
        # ('etat_civil', '0009_previous_migration'), # Commenté car l'app est nouvelle dans notre repo
    ]

    operations = [
        migrations.CreateModel(
            name='ProfilAgent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialites', models.JSONField(default=list)),
                ('disponibilite', models.BooleanField(default=True)),
                ('charge_maximale', models.PositiveIntegerField(default=10)),
                ('score_global', models.FloatField(default=0.0)),
                ('temps_moyen_traitement', models.FloatField(default=0.0)),
                ('taux_reussite', models.FloatField(default=0.0)),
                ('taux_respect_delais', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profil_agent', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'attribution_profil_agent',
            },
        ),
        migrations.CreateModel(
            name='JournalAttribution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle_action', models.CharField(max_length=255)),
                ('dossier_id', models.CharField(max_length=100)),
                ('agent_avant', models.CharField(blank=True, max_length=255, null=True)),
                ('agent_apres', models.CharField(blank=True, max_length=255, null=True)),
                ('score_calcule', models.FloatField(default=0.0)),
                ('justification', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('metadata', models.JSONField(default=dict)),
                ('responsable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='actions_journal', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'attribution_journal',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='AttributionDossier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score_attribution', models.FloatField(default=0.0)),
                ('niveau_priorite', models.CharField(choices=[('urgent', 'Urgent'), ('eleve', 'Élevé'), ('normal', 'Normal'), ('faible', 'Faible')], default='normal', max_length=20)),
                ('source_attribution', models.CharField(choices=[('auto', 'Automatique'), ('ia', 'Intelligence Artificielle'), ('manuel', 'Manuel'), ('reattribution', 'Réattribution'), ('superviseur', 'Superviseur')], default='auto', max_length=20)),
                ('justification_ia', models.TextField(blank=True, null=True)),
                ('date_attribution', models.DateTimeField(auto_now_add=True)),
                ('date_limite_traitement', models.DateTimeField()),
                ('notification_24h_envoyee', models.BooleanField(default=False)),
                ('notification_48h_envoyee', models.BooleanField(default=False)),
                ('est_reattribution', models.BooleanField(default=False)),
                ('agent_actuel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributions_actuelles', to=settings.AUTH_USER_MODEL)),
                ('ancien_agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='anciennes_attributions', to=settings.AUTH_USER_MODEL)),
                ('dossier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributions', to='dossiers.dossier')),
                ('responsable_attribution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attributions_effectuees', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'attribution_dossier',
            },
        ),
    ]
