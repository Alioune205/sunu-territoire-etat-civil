"""
Modèles avancés pour le système de répartition et d'attribution intelligente des dossiers.
Conçu pour l'excellence architecturale : Constraints de base de données, Indexation optimale, et Logique encapsulée.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, F, CheckConstraint, UniqueConstraint
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from apps.shared.models import TimeStampedModel
from apps.dossiers.models import Dossier


class ProfilAgent(TimeStampedModel):
    """
    Extension du modèle utilisateur pour les agents d'état civil.
    Gère les métriques de performance, la disponibilité et les compétences pour le routage.
    """
    
    class Status(models.TextChoices):
        EN_LIGNE = 'en_ligne', 'En Ligne (Disponible)'
        EN_PAUSE = 'en_pause', 'En Pause'
        HORS_LIGNE = 'hors_ligne', 'Hors Ligne'
        SURCHARGE = 'surcharge', 'Surchargé (Ne pas déranger)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profil_attribution',
        verbose_name="Utilisateur Agent"
    )
    
    # --- État & Capacité ---
    statut_actuel = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.HORS_LIGNE,
        db_index=True,
        verbose_name="Statut Actuel"
    )
    capacite_maximale = models.PositiveIntegerField(
        default=15,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name="Capacité max de dossiers simultanés",
        help_text="Le nombre de dossiers que cet agent peut gérer en parallèle."
    )
    
    # --- Compétences Spécialisées ---
    competences_types_dossiers = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Compétences (Types de dossiers supportés)",
        help_text="Liste des types de dossiers que cet agent est habilité à traiter (ex: ['birth_certificate', 'marriage_certificate'])."
    )
    
    # --- Métriques de Performance (Pour le Moteur de Scoring) ---
    score_performance_global = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Score de Performance Global",
        help_text="Calculé automatiquement par le moteur de scoring (Qualité + Rapidité)."
    )
    temps_moyen_traitement_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name="Temps moyen de traitement (minutes)",
        help_text="Sert à évaluer la charge cognitive prévisionnelle de l'agent."
    )
    dossiers_traites_historique = models.PositiveIntegerField(
        default=0,
        verbose_name="Total Historique de Dossiers Traités"
    )

    class Meta:
        verbose_name = "Profil d'Attribution Agent"
        verbose_name_plural = "Profils d'Attribution Agents"
        ordering = ['-score_performance_global', 'user__last_name']
        indexes = [
            models.Index(fields=['statut_actuel', 'score_performance_global']),
        ]
        constraints = [
            CheckConstraint(
                check=Q(score_performance_global__gte=0.0) & Q(score_performance_global__lte=100.0),
                name='etat_civil_profilagent_valid_score'
            ),
            CheckConstraint(
                check=Q(capacite_maximale__gte=1) & Q(capacite_maximale__lte=50),
                name='etat_civil_profilagent_valid_capacity'
            ),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.get_statut_actuel_display()} (Score: {self.score_performance_global})"

    @property
    def charge_actuelle(self):
        """Calcule le nombre de dossiers actuellement en cours pour cet agent."""
        return self.attributions.filter(statut=AttributionDossier.Status.EN_COURS).count()

    @property
    def est_disponible(self):
        """Vérifie si l'agent peut recevoir un nouveau dossier."""
        return (
            self.statut_actuel == self.Status.EN_LIGNE 
            and self.charge_actuelle < self.capacite_maximale
        )


class AttributionDossier(TimeStampedModel):
    """
    Gère la relation d'attribution entre un dossier et un agent.
    Inclut les contraintes de SLA (Service Level Agreement) et les priorités dynamiques.
    """
    
    class Status(models.TextChoices):
        ATTRIBUE = 'attribue', 'Attribué (Non ouvert)'
        EN_COURS = 'en_cours', 'En Cours de Traitement'
        TERMINE = 'termine', 'Traitement Terminé'
        ESCALADE = 'escalade', 'Escaladé (SLA Dépassé)'
        REATTRIBUE = 'reattribue', 'Réattribué à un autre agent'

    class PriorityLevel(models.IntegerChoices):
        BASSE = 1, 'Basse'
        NORMALE = 2, 'Normale'
        HAUTE = 3, 'Haute'
        URGENTE = 4, 'Urgente (Alerte)'
        CRITIQUE = 5, 'Critique (Escalade Supérieure)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='attributions_historique',
        verbose_name="Dossier"
    )
    agent = models.ForeignKey(
        ProfilAgent,
        on_delete=models.CASCADE,
        related_name='attributions',
        verbose_name="Agent Assigné"
    )
    
    # --- Suivi & SLA ---
    statut = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ATTRIBUE,
        db_index=True,
        verbose_name="Statut de l'Attribution"
    )
    niveau_priorite = models.IntegerField(
        choices=PriorityLevel.choices,
        default=PriorityLevel.NORMALE,
        db_index=True,
        verbose_name="Niveau de Priorité"
    )
    
    date_limite_sla = models.DateTimeField(
        verbose_name="Date Limite SLA",
        help_text="Date à laquelle le dossier doit impérativement être traité avant escalade."
    )
    date_traitement_effectif = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Date de Traitement Effectif"
    )
    
    # --- Métriques d'Attribution ---
    score_matching_initial = models.FloatField(
        default=0.0,
        verbose_name="Score de Matching Initial",
        help_text="Le score généré par l'algorithme justifiant cette attribution."
    )

    class Meta:
        verbose_name = "Attribution de Dossier"
        verbose_name_plural = "Attributions de Dossiers"
        ordering = ['-niveau_priorite', 'date_limite_sla']
        indexes = [
            models.Index(fields=['statut', 'niveau_priorite']),
            models.Index(fields=['agent', 'statut']),
            models.Index(fields=['date_limite_sla']),
        ]
        constraints = [
            UniqueConstraint(
                fields=['dossier'],
                condition=Q(statut__in=['attribue', 'en_cours']),
                name='etat_civil_unique_active_attribution_per_dossier'
            )
        ]

    def __str__(self):
        return f"Dossier {self.dossier.reference} -> {self.agent.user.last_name} ({self.get_statut_display()})"

    def clean(self):
        super().clean()
        if not self.date_limite_sla:
            # Règle Métier par défaut : SLA de 48 heures si non défini
            self.date_limite_sla = timezone.now() + timezone.timedelta(hours=48)
            
        # Validation anti-conflit de capacité
        if self.statut in [self.Status.ATTRIBUE, self.Status.EN_COURS] and not self.agent.est_disponible:
            raise ValidationError(f"L'agent {self.agent.user.last_name} a atteint sa capacité maximale ou est hors ligne.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        # SYNCHRONISATION ABSOLUE AVEC LE MODÈLE D'ALIOUNE (Anti-Conflit)
        # On s'assure que le champ `assigned_agent` natif de `Dossier` est toujours aligné avec notre attribution
        if self.statut in [self.Status.ATTRIBUE, self.Status.EN_COURS]:
            if self.dossier.assigned_agent != self.agent.user:
                self.dossier.assigned_agent = self.agent.user
                self.dossier.save(update_fields=['assigned_agent'])
        elif self.statut in [self.Status.REATTRIBUE, self.Status.ESCALADE]:
            if self.dossier.assigned_agent == self.agent.user:
                self.dossier.assigned_agent = None
                self.dossier.save(update_fields=['assigned_agent'])

    @property
    def est_en_retard(self):
        """Indique si le SLA est dépassé par rapport à l'heure actuelle."""
        if self.statut in [self.Status.TERMINE, self.Status.REATTRIBUE]:
            return False
        return timezone.now() > self.date_limite_sla


class JournalAttribution(TimeStampedModel):
    """
    Audit Trail (Journalisation) indestructible pour tracer chaque mouvement d'un dossier.
    Garantit la transparence totale des actions de réattribution (exigence légale).
    """
    
    class Action(models.TextChoices):
        ATTRIBUTION_INITIALE = 'attribution_initiale', 'Attribution Initiale'
        CHANGEMENT_STATUT = 'changement_statut', 'Changement de Statut'
        REATTRIBUTION_MANUELLE = 'reattribution_manuelle', 'Réattribution Manuelle'
        REATTRIBUTION_AUTOMATIQUE = 'reattribution_automatique', 'Réattribution Automatique (Moteur)'
        ESCALADE_SLA = 'escalade_sla', 'Escalade de SLA'
        TIMEOUT_AGENT = 'timeout_agent', 'Délai d\'inactivité dépassé'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='journal_attributions',
        verbose_name="Dossier"
    )
    agent_concerne = models.ForeignKey(
        ProfilAgent,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='historique_actions',
        verbose_name="Agent Concerné"
    )
    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        db_index=True,
        verbose_name="Action effectuée"
    )
    motif_detaille = models.TextField(
        verbose_name="Motif Détaillé de l'Action",
        help_text="Explication technique ou métier justifiant l'action."
    )
    anciennes_valeurs = models.JSONField(
        default=dict, blank=True,
        verbose_name="Anciennes Valeurs",
        help_text="Snapshot des données avant la modification (pour la traçabilité complète)."
    )

    class Meta:
        verbose_name = "Journal d'Attribution"
        verbose_name_plural = "Journaux d'Attribution"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dossier', 'action']),
        ]

    def __str__(self):
        return f"[{self.get_action_display()}] {self.dossier.reference} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
