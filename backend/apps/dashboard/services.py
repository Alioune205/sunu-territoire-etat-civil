"""
Dashboard services — toute la logique d'agrégation ORM pour le dashboard.
DEV 2A: Pape Alioune Sène

Chemin : backend/apps/dashboard/services.py
Rôle   : Centralise les requêtes SQL optimisées (Count, Avg, annotations).
         Aucune logique métier dans les views — tout passe par ces fonctions.
Impact : Lecture seule sur les modèles existants. Aucune migration requise.

Principes appliqués :
  - select_related / prefetch_related pour éviter les requêtes N+1
  - Agrégations DB (Count, Avg, ExpressionWrapper) plutôt que boucles Python
  - Filtrage par commune pour les agents non-super_admin
"""
from django.db.models import (
    Count, Avg, Q, F, ExpressionWrapper,
    FloatField, IntegerField, DurationField,
)
from django.db.models.functions import (
    TruncDate, TruncWeek, TruncHour,
    ExtractHour,
)
from django.utils import timezone
from datetime import timedelta

from apps.dossiers.models import Dossier
from apps.audit_logs.models import AuditLog
from apps.communes.models import Commune


# ---------------------------------------------------------------------------
# Helpers internes
# ---------------------------------------------------------------------------

def _hours_from_duration(avg_duration):
    """Convertit une durée moyenne (timedelta ou None) en heures (float ou None)."""
    if avg_duration is None:
        return None
    total_seconds = avg_duration.total_seconds()
    return round(total_seconds / 3600, 2)


def _dossier_queryset_for_user(user):
    """
    Retourne le queryset de base filtré selon le rôle de l'utilisateur.
    - super_admin → tous les dossiers
    - civil_admin, agents → dossiers de leur commune
    - autres → aucun (le dashboard n'est pas destiné aux citoyens)
    """
    qs = Dossier.objects.select_related('commune', 'citizen', 'assigned_agent')
    if user.role == 'super_admin':
        return qs.all()
    elif user.commune_id:
        return qs.filter(commune=user.commune)
    return qs.none()


# ---------------------------------------------------------------------------
# SERVICE 1 : Stats globales
# ---------------------------------------------------------------------------

def get_dashboard_stats(user):
    """
    Retourne les statistiques globales du dashboard.
    Données structurées pour DashboardStatsSerializer.
    """
    from apps.users.models import User

    qs = _dossier_queryset_for_user(user)

    total_dossiers = qs.count()

    # Répartition par statut — une seule requête SQL GROUP BY
    status_counts_qs = (
        qs.values('status')
          .annotate(count=Count('id'))
          .order_by('status')
    )
    status_display_map = dict(Dossier.Status.choices)
    by_status = [
        {
            'status': row['status'],
            'status_display': status_display_map.get(row['status'], row['status']),
            'count': row['count'],
        }
        for row in status_counts_qs
    ]

    # Répartition par type d'acte — une seule requête SQL GROUP BY
    type_counts_qs = (
        qs.values('type')
          .annotate(count=Count('id'))
          .order_by('type')
    )
    type_display_map = dict(Dossier.Type.choices)
    by_type = [
        {
            'type': row['type'],
            'type_display': type_display_map.get(row['type'], row['type']),
            'count': row['count'],
        }
        for row in type_counts_qs
    ]

    # Totaux users et communes (globaux, pas filtrés par commune)
    if user.role == 'super_admin':
        total_users = User.objects.filter(is_active=True).count()
        total_communes = Commune.objects.count()
    else:
        # Pour un admin de commune, on compte les users de sa commune
        total_users = User.objects.filter(
            commune=user.commune, is_active=True
        ).count() if user.commune_id else 0
        total_communes = 1 if user.commune_id else 0

    return {
        'total_dossiers': total_dossiers,
        'total_users': total_users,
        'total_communes': total_communes,
        'by_status': by_status,
        'by_type': by_type,
    }


# ---------------------------------------------------------------------------
# SERVICE 2 : KPIs
# ---------------------------------------------------------------------------

def get_dashboard_kpis(user):
    """
    Calcule les KPIs de performance.
    - Temps moyen de traitement par commune (submitted_at → completed_at)
    - Taux de rejet global et par commune
    - Productivité des agents

    Note : Le calcul de durée utilise ExpressionWrapper sur la différence
    de DateTimeField — compatible PostgreSQL. Le résultat avg_duration est
    un timedelta converti en heures pour la lisibilité.
    """
    from apps.users.models import User

    qs = _dossier_queryset_for_user(user)

    # ---- Taux de rejet global ----
    total = qs.count()
    rejected_total = qs.filter(status=Dossier.Status.REJECTED).count()
    global_rejection_rate = round(
        (rejected_total / total * 100) if total > 0 else 0.0, 2
    )

    # ---- Temps moyen global (dossiers completed uniquement) ----
    completed_qs = qs.filter(
        status=Dossier.Status.COMPLETED,
        submitted_at__isnull=False,
        completed_at__isnull=False,
    ).annotate(
        processing_duration=ExpressionWrapper(
            F('completed_at') - F('submitted_at'),
            output_field=DurationField(),
        )
    )
    avg_duration_global = completed_qs.aggregate(
        avg=Avg('processing_duration')
    )['avg']
    global_avg_processing_hours = _hours_from_duration(avg_duration_global)

    # ---- KPIs par commune ----
    # CORRECTION B-01 : une seule requête SQL GROUP BY au lieu de N+1.
    # Le temps moyen est calculé via annotate() sur le queryset complet,
    # puis récupéré via un dict en Python — zéro requête supplémentaire.

    # Étape 1 : temps moyen par commune en une requête (dossiers completed only)
    avg_by_commune_qs = (
        qs.filter(
            status=Dossier.Status.COMPLETED,
            submitted_at__isnull=False,
            completed_at__isnull=False,
        )
        .annotate(
            processing_duration=ExpressionWrapper(
                F('completed_at') - F('submitted_at'),
                output_field=DurationField(),
            )
        )
        .values('commune__id')
        .annotate(avg_dur=Avg('processing_duration'))
    )
    avg_duration_map = {
        row['commune__id']: row['avg_dur']
        for row in avg_by_commune_qs
    }

    # Étape 2 : totaux par commune en une requête GROUP BY
    communes_scope = (
        qs.values('commune__id', 'commune__name')
          .annotate(
              total_dossiers=Count('id'),
              approved_count=Count('id', filter=Q(status=Dossier.Status.APPROVED)),
              rejected_count=Count('id', filter=Q(status=Dossier.Status.REJECTED)),
          )
          .order_by('commune__name')
    )

    # Étape 3 : assemblage en Python — aucune requête DB ici
    by_commune = []
    for row in communes_scope:
        total_c = row['total_dossiers']
        rejected_c = row['rejected_count']
        rejection_rate = round(
            (rejected_c / total_c * 100) if total_c > 0 else 0.0, 2
        )
        avg_dur = avg_duration_map.get(row['commune__id'])

        by_commune.append({
            'commune_id': row['commune__id'],
            'commune_name': row['commune__name'],
            'avg_processing_hours': _hours_from_duration(avg_dur),
            'total_dossiers': total_c,
            'approved_count': row['approved_count'],
            'rejected_count': rejected_c,
            'rejection_rate_percent': rejection_rate,
        })

    # ---- Productivité des agents ----
    # CORRECTION B-02 : remplacer la boucle (4 requêtes/agent) par une seule
    # requête annotée sur le queryset User. Django génère un seul SQL avec
    # COUNT + COUNT FILTER + COUNT FILTER — zéro N+1.

    agent_roles = [
        'reception_agent',
        'verification_agent',
        'civil_admin',
        'super_admin',
    ]
    agents_base_qs = User.objects.filter(role__in=agent_roles, is_active=True)
    if user.role != 'super_admin' and user.commune_id:
        agents_base_qs = agents_base_qs.filter(commune=user.commune)

    # Toutes les annotations en une seule requête SQL
    agents_annotated = (
        agents_base_qs
        .select_related('commune')
        .annotate(
            dossiers_handled=Count(
                'assigned_dossiers',
                filter=Q(assigned_dossiers__in=qs),
            ),
            approved=Count(
                'assigned_dossiers',
                filter=Q(
                    assigned_dossiers__in=qs,
                    assigned_dossiers__status=Dossier.Status.APPROVED,
                ),
            ),
            rejected=Count(
                'assigned_dossiers',
                filter=Q(
                    assigned_dossiers__in=qs,
                    assigned_dossiers__status=Dossier.Status.REJECTED,
                ),
            ),
        )
        .filter(dossiers_handled__gt=0)
        .order_by('-dossiers_handled')
    )

    # Temps moyen par agent en une requête séparée (GROUP BY assigned_agent)
    agent_avg_qs = (
        qs.filter(
            status=Dossier.Status.COMPLETED,
            submitted_at__isnull=False,
            completed_at__isnull=False,
            assigned_agent__isnull=False,
        )
        .annotate(
            processing_duration=ExpressionWrapper(
                F('completed_at') - F('submitted_at'),
                output_field=DurationField(),
            )
        )
        .values('assigned_agent__id')
        .annotate(avg_dur=Avg('processing_duration'))
    )
    agent_avg_map = {
        row['assigned_agent__id']: row['avg_dur']
        for row in agent_avg_qs
    }

    # Assemblage en Python — aucune requête DB ici
    agent_productivity = [
        {
            'agent_id': agent.id,
            'agent_name': agent.full_name,
            'commune_name': agent.commune.name if agent.commune else None,
            'dossiers_handled': agent.dossiers_handled,
            'approved': agent.approved,
            'rejected': agent.rejected,
            'avg_processing_hours': _hours_from_duration(
                agent_avg_map.get(agent.id)
            ),
        }
        for agent in agents_annotated
    ]

    # ---- Dossiers en attente depuis plus de 48h (indicateur SLA) ----
    cutoff_48h = timezone.now() - timedelta(hours=48)
    pending_over_48h = qs.filter(
        status__in=[Dossier.Status.SUBMITTED, Dossier.Status.IN_REVIEW],
        submitted_at__lt=cutoff_48h,
    ).count()

    return {
        'global_rejection_rate_percent': global_rejection_rate,
        'global_avg_processing_hours': global_avg_processing_hours,
        'pending_over_48h': pending_over_48h,
        'by_commune': by_commune,
        'agent_productivity': agent_productivity,
    }


# ---------------------------------------------------------------------------
# SERVICE 3 : Charts
# ---------------------------------------------------------------------------

def get_dashboard_charts(user, days: int = 30):
    """
    Retourne les données pour les graphiques de tendances.
    - Volume journalier sur les N derniers jours
    - Volume hebdomadaire sur les N derniers jours
    - Activité par heure (tous les temps combinés)

    Paramètre `days` : fenêtre temporelle (défaut 30j, max 365j).
    """
    days = min(max(days, 7), 365)
    since = timezone.now() - timedelta(days=days)

    qs = _dossier_queryset_for_user(user).filter(created_at__gte=since)

    # ---- Volume journalier ----
    daily_qs = (
        qs.annotate(date=TruncDate('created_at'))
          .values('date')
          .annotate(count=Count('id'))
          .order_by('date')
    )
    daily_volume = [
        {'date': row['date'], 'count': row['count']}
        for row in daily_qs
    ]

    # ---- Volume hebdomadaire ----
    weekly_qs = (
        qs.annotate(week=TruncWeek('created_at'))
          .values('week')
          .annotate(count=Count('id'))
          .order_by('week')
    )
    weekly_volume = [
        {
            'week': row['week'].strftime('%Y-W%W') if row['week'] else '',
            'count': row['count'],
        }
        for row in weekly_qs
    ]

    # ---- Activité horaire (pattern de soumission dans la journée) ----
    # On utilise tous les dossiers (pas de limite temporelle) pour un profil fiable
    all_qs = _dossier_queryset_for_user(user)
    hourly_qs = (
        all_qs.annotate(hour=ExtractHour('created_at'))
              .values('hour')
              .annotate(count=Count('id'))
              .order_by('hour')
    )
    # Remplir les heures manquantes avec 0
    hourly_map = {row['hour']: row['count'] for row in hourly_qs}
    hourly_activity = [
        {'hour': h, 'count': hourly_map.get(h, 0)}
        for h in range(24)
    ]

    return {
        'daily_volume': daily_volume,
        'weekly_volume': weekly_volume,
        'hourly_activity': hourly_activity,
    }


# ---------------------------------------------------------------------------
# SERVICE 4 : Activity feed (AuditLog)
# ---------------------------------------------------------------------------

def get_recent_activity(user, limit: int = 20):
    """
    Retourne les N derniers logs d'activité du système.
    Super admin → tous les logs.
    Autres → logs liés aux utilisateurs de leur commune.
    """
    limit = min(max(limit, 5), 100)

    qs = AuditLog.objects.select_related('user', 'user__commune')

    if user.role != 'super_admin' and user.commune_id:
        # Filtrer sur les utilisateurs de la même commune
        qs = qs.filter(
            Q(user__commune=user.commune) | Q(user=user)
        )

    qs = qs.order_by('-created_at')[:limit]

    action_display_map = dict(AuditLog.Action.choices)

    result = []
    for log in qs:
        result.append({
            'id': log.id,
            'user_name': log.user.full_name if log.user else None,
            'user_email': log.user.email if log.user else None,
            'user_role': log.user.role if log.user else None,
            'action': log.action,
            'action_display': action_display_map.get(log.action, log.action),
            'resource_type': log.resource_type,
            'resource_id': log.resource_id,
            'details': log.details,
            'ip_address': str(log.ip_address) if log.ip_address else None,
            'created_at': log.created_at,
        })

    return result