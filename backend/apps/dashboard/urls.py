"""
URL configuration for Dashboard — Statistiques et rapports.
"""
from django.urls import path

from .views import (
    OverviewView,
    CountByStatusView,
    CountByTypeView,
    CountByCommuneView,
    DailyVolumeView,
    AgentPerformanceView,
    ProcessingDelaysView,
    RecentDossiersView,
    StaleDossiersView,
)

app_name = 'dashboard'

urlpatterns = [
    path('overview/', OverviewView.as_view(), name='overview'),
    path('by-status/', CountByStatusView.as_view(), name='by-status'),
    path('by-type/', CountByTypeView.as_view(), name='by-type'),
    path('by-commune/', CountByCommuneView.as_view(), name='by-commune'),
    path('daily-volume/', DailyVolumeView.as_view(), name='daily-volume'),
    path('agent-performance/', AgentPerformanceView.as_view(), name='agent-performance'),
    path('processing-delays/', ProcessingDelaysView.as_view(), name='processing-delays'),
    path('recent/', RecentDossiersView.as_view(), name='recent'),
    path('stale/', StaleDossiersView.as_view(), name='stale'),
]
