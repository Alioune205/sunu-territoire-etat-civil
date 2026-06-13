"""
Moteur de Scoring - Intelligence Artificielle (Heuristique) pour la répartition des dossiers.
Calcule la pertinence d'un agent pour un dossier donné selon 5 critères de pointe.
"""
from django.db.models import Count, Q
from django.utils import timezone
from apps.etat_civil.models_attribution import ProfilAgent, AttributionDossier
from apps.dossiers.models import Dossier

class MoteurScoring:
    """
    Algorithme de calcul du Score de Matching (0 à 100) pour déterminer le meilleur agent.
    Pondérations strictes :
    - Disponibilité (Charge actuelle vs Capacité) : 35%
    - Compétence (Type de dossier matché) : 30%
    - Performance (Score global historique) : 20%
    - Vitesse (Temps moyen de traitement) : 15%
    """

    POIDS_CHARGE = 0.35
    POIDS_COMPETENCE = 0.30
    POIDS_PERFORMANCE = 0.20
    POIDS_VITESSE = 0.15

    @classmethod
    def evaluer_agent_pour_dossier(cls, agent: ProfilAgent, dossier: Dossier) -> float:
        """
        Évalue un agent spécifique pour un dossier donné.
        Renvoie un score sur 100.0. Si le score est 0.0, l'agent est inéligible.
        """
        # 1. Filtre strict (Hard Constraints)
        if not agent.est_disponible:
            return 0.0
            
        # Vérification des compétences (Si défini)
        if agent.competences_types_dossiers and dossier.type not in agent.competences_types_dossiers:
            return 0.0

        # 2. Score de Disponibilité (0-100)
        # Utilisation de la charge pré-calculée en SQL si disponible (optimisation), sinon fallback sur la property
        charge = getattr(agent, 'charge_actuelle_optimisee', agent.charge_actuelle)
        ratio_charge = charge / agent.capacite_maximale
        score_disponibilite = (1.0 - ratio_charge) * 100.0

        # 3. Score de Compétence Spécialisée (0-100)
        # 100 si le type exact correspond, 50 par défaut si l'agent est généraliste (compétences vides)
        score_competence = 100.0 if agent.competences_types_dossiers else 50.0

        # 4. Score de Performance (0-100)
        # Directement pris depuis le profil (qui est lui-même mis à jour périodiquement)
        score_performance = agent.score_performance_global

        # 5. Score de Vitesse (0-100)
        # Basé sur une constante métier (ex: 60 min est lent, 10 min est très rapide)
        temps_max_theorique = 60.0
        temps_agent = min(agent.temps_moyen_traitement_minutes, temps_max_theorique)
        score_vitesse = ((temps_max_theorique - temps_agent) / temps_max_theorique) * 100.0

        # Calcul Final Pondéré
        score_final = (
            (score_disponibilite * cls.POIDS_CHARGE) +
            (score_competence * cls.POIDS_COMPETENCE) +
            (score_performance * cls.POIDS_PERFORMANCE) +
            (score_vitesse * cls.POIDS_VITESSE)
        )

        return round(score_final, 2)

    @classmethod
    def trouver_meilleur_agent(cls, dossier: Dossier) -> tuple[ProfilAgent, float]:
        """
        Parcourt tous les agents éligibles de la commune du dossier et retourne le meilleur match.
        Renvoie (Agent, Score). Retourne (None, 0.0) si aucun agent n'est disponible.
        """
        # Filtrer d'abord les agents de la même commune
        # OPTIMISATION EXTRÊME : Éviter le problème N+1 avec Count et Q dans la base de données (SQL pur)
        agents_potentiels = ProfilAgent.objects.filter(
            statut_actuel=ProfilAgent.Status.EN_LIGNE,
            user__commune=dossier.commune
        ).annotate(
            charge_calculee_sql=Count(
                'attributions', 
                filter=Q(attributions__statut=AttributionDossier.Status.EN_COURS)
            )
        ).select_related('user')

        meilleur_agent = None
        meilleur_score = 0.0

        for agent in agents_potentiels:
            # Surcharge dynamique de la propriété pour utiliser la valeur calculée en SQL
            agent.charge_actuelle_optimisee = agent.charge_calculee_sql
            
            score = cls.evaluer_agent_pour_dossier(agent, dossier)
            if score > meilleur_score:
                meilleur_score = score
                meilleur_agent = agent

        return meilleur_agent, meilleur_score
