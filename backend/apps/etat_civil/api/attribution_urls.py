from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .attribution_views import AttributionViewSet

router = DefaultRouter()
router.register(r'attributions', AttributionViewSet, basename='attribution')

urlpatterns = [
    path('', include(router.urls)),
]
