"""
Dashboard filters — filtrage avancé des dossiers pour le dashboard.
DEV 2A: Pape Alioune Sène

Chemin : backend/apps/dashboard/filters.py
Rôle   : Fournit des filtres puissants pour affiner les données renvoyées
         par les endpoints dashboard (par commune, statut, type, agent, dates).
Impact : Aucune modification des modèles. S'appuie sur django-filter déjà installé.
"""
import django_filters
from django.db.models import Q

from apps.dossiers.models import Dossier
from apps.audit_logs.models import AuditLog


class DossierDashboardFilter(django_filters.FilterSet):
    """
    Filtre avancé pour les dossiers dans le contexte dashboard.
    Utilisable depuis n'importe quel endpoint qui consomme le queryset Dossier.

    Paramètres URL supportés :
      ?commune=<uuid>
      ?status=submitted
      ?type=birth_certificate
      ?assigned_agent=<uuid>
      ?date_from=2026-01-01
      ?date_to=2026-06-30
      ?search=SNCV-2026   (recherche sur référence, prénom, nom, CNI)
    """

    commune = django_filters.UUIDFilter(field_name='commune__id')
    status = django_filters.ChoiceFilter(choices=Dossier.Status.choices)
    type = django_filters.ChoiceFilter(choices=Dossier.Type.choices)
    assigned_agent = django_filters.UUIDFilter(field_name='assigned_agent__id')

    # Plage de dates sur la date de création
    date_from = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__gte',
        label='Créé après (YYYY-MM-DD)',
    )
    date_to = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__lte',
        label='Créé avant (YYYY-MM-DD)',
    )

    # Plage de dates sur la soumission
    submitted_from = django_filters.DateFilter(
        field_name='submitted_at',
        lookup_expr='date__gte',
        label='Soumis après (YYYY-MM-DD)',
    )
    submitted_to = django_filters.DateFilter(
        field_name='submitted_at',
        lookup_expr='date__lte',
        label='Soumis avant (YYYY-MM-DD)',
    )

    # Recherche textuelle multi-champs (référence, nom, CNI)
    search = django_filters.CharFilter(
        method='filter_search',
        label='Recherche (référence, nom, CNI)',
    )

    class Meta:
        model = Dossier
        fields = [
            'commune',
            'status',
            'type',
            'assigned_agent',
            'date_from',
            'date_to',
            'submitted_from',
            'submitted_to',
            'search',
        ]

    def filter_search(self, queryset, name, value):
        """
        Recherche textuelle sur :
        - reference (numéro de dossier)
        - citizen__first_name
        - citizen__last_name
        - citizen__profile__cni_number (via CitizenProfile)
        """
        if not value:
            return queryset
        return queryset.filter(
            Q(reference__icontains=value) |
            Q(citizen__first_name__icontains=value) |
            Q(citizen__last_name__icontains=value) |
            Q(citizen__profile__cni_number__icontains=value)
        ).distinct()


class AuditLogDashboardFilter(django_filters.FilterSet):
    """
    Filtre pour les logs d'audit dans le dashboard.

    Paramètres URL supportés :
      ?action=LOGIN
      ?resource_type=dossier
      ?user=<uuid>
      ?date_from=2026-01-01
      ?date_to=2026-06-30
    """

    action = django_filters.ChoiceFilter(choices=AuditLog.Action.choices)
    resource_type = django_filters.CharFilter(lookup_expr='iexact')
    user = django_filters.UUIDFilter(field_name='user__id')

    date_from = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__gte',
    )
    date_to = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__lte',
    )

    class Meta:
        model = AuditLog
        fields = ['action', 'resource_type', 'user', 'date_from', 'date_to']
