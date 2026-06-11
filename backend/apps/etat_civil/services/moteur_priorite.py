"""
Moteur de Priorité - Calcul automatisé des niveaux d'urgence et des SLA.
"""
from django.utils import timezone
from apps.dossiers.models import Dossier
from apps.etat_civil.models_attribution import AttributionDossier

class MoteurPriorite:
    """
    Détermine le niveau de priorité et le délai SLA (Service Level Agreement) 
    d'un dossier en fonction de son type, de son ancienneté, et des métadonnées.
    """

    # Définition des SLA par type de dossier (en heures)
    SLA_PAR_DEFAUT = 48
    SLA_MAPPING = {
        Dossier.Type.DEATH_CERTIFICATE: 12,     # Très urgent (inhumation)
        Dossier.Type.BIRTH_CERTIFICATE: 48,     # Standard
        Dossier.Type.MARRIAGE_CERTIFICATE: 72,  # Moins urgent
        Dossier.Type.RESIDENCE_CERTIFICATE: 24, # Rapide
    }

    @classmethod
    def calculer_priorite(cls, dossier: Dossier) -> int:
        """
        Calcule la priorité (1 = Basse à 5 = Critique) d'un dossier.
        """
        priorite_base = AttributionDossier.PriorityLevel.NORMALE

        # 1. Règle Métier : Les décès sont d'une priorité absolue
        if dossier.type == Dossier.Type.DEATH_CERTIFICATE:
            priorite_base = AttributionDossier.PriorityLevel.URGENTE

        # 2. Règle Métier : Les jugements supplétifs prennent plus de temps mais sont urgents juridiquement
        metadata = dossier.metadata or {}
        if metadata.get('jugement_suppletif') is True:
            priorite_base = AttributionDossier.PriorityLevel.HAUTE

        # 3. Augmentation avec le temps (Si le dossier est vieux, sa priorité augmente)
        # (Cette logique est souvent utilisée dans un script Cron pour augmenter la priorité des vieux dossiers)
        if dossier.submitted_at:
            heures_depuis_soumission = (timezone.now() - dossier.submitted_at).total_seconds() / 3600
            if heures_depuis_soumission > 48:
                # Si plus de 48h d'attente, on force l'urgence
                priorite_base = max(priorite_base, AttributionDossier.PriorityLevel.URGENTE)

        return priorite_base

    @classmethod
    def calculer_date_limite_sla(cls, dossier: Dossier) -> timezone.datetime:
        """
        Calcule la date de fin de la SLA selon le type de dossier.
        """
        heures_allouees = cls.SLA_MAPPING.get(dossier.type, cls.SLA_PAR_DEFAUT)
        
        # Le point de départ est la date de soumission. Si absent, c'est "maintenant".
        date_depart = dossier.submitted_at if dossier.submitted_at else timezone.now()
        
        return date_depart + timezone.timedelta(hours=heures_allouees)
