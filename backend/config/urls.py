"""
SUNU CIVIL — URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Core APIs
    path('api/auth/', include('apps.authentication.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/roles/', include('apps.roles.urls')),
    path('api/communes/', include('apps.communes.urls')),
    path('api/dossiers/', include('apps.dossiers.urls')),
    path('api/documents/', include('apps.documents.urls')),
    path('api/audit-logs/', include('apps.audit_logs.urls')),

    # Stub APIs (for DEV 2)
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/qr/', include('apps.qr.urls')),
    path('api/ai/', include('apps.ai.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
