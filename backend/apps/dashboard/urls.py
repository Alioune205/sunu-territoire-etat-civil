"""
URL configuration for Dashboard — DEV 2A: Pape Alioune Sène

Chemin : backend/apps/dashboard/urls.py
Rôle   : Mappe les 6 endpoints dashboard sur leurs views.

IMPORTANT : Ce fichier REMPLACE le stub vide existant.
            Il est déjà inclus dans config/urls.py via :
            path('api/dashboard/', include('apps.dashboard.urls'))
            → NE PAS modifier config/urls.py.

Endpoints exposés :
  GET /api/dashboard/stats/           → Statistiques globales
  GET /api/dashboard/kpis/            → KPIs de performance
  GET /api/dashboard/charts/          → Données graphiques
  GET /api/dashboard/activity/        → Flux d'audit complet
  GET /api/dashboard/recent-actions/  → Dernières actions importantes
  GET /api/dashboard/search/          → Recherche et filtrage avancés
"""
from django.urls import path

from .views import (
    DashboardStatsView,
    DashboardKPIsView,
    DashboardChartsView,
    DashboardActivityView,
    DashboardRecentActionsView,
    DashboardSearchView,
)

app_name = 'dashboard'

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='stats'),
    path('kpis/', DashboardKPIsView.as_view(), name='kpis'),
    path('charts/', DashboardChartsView.as_view(), name='charts'),
    path('activity/', DashboardActivityView.as_view(), name='activity'),
    path('recent-actions/', DashboardRecentActionsView.as_view(), name='recent-actions'),
    path('search/', DashboardSearchView.as_view(), name='search'),
]
