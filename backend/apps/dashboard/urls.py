"""
URL configuration for the Dashboard app.
"""
from django.urls import path
from .views import (
    DashboardStatsView,
    GlobalStatsView,
    PerformanceStatsView,
    ActivityStatsView,
)

urlpatterns = [
    path(
        'stats/',
        DashboardStatsView.as_view(),
        name='dashboard-stats'
    ),
    path(
        'global-stats/',
        GlobalStatsView.as_view(),
        name='global-stats'
    ),
    path(
        'performance/',
        PerformanceStatsView.as_view(),
        name='performance-stats'
    ),
    path(
        'activity/',
        ActivityStatsView.as_view(),
        name='activity-stats'
    ),
]
