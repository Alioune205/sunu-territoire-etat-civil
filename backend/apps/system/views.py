"""
System views — Health check, monitoring, métriques système et gestion des logs.

Endpoints :
    - GET /api/system/health/    → Public, utilisé par les outils de monitoring
    - GET /api/system/metrics/   → Super admin uniquement, métriques avancées
    - GET /api/system/logs/      → Super admin uniquement, journal système
"""
import time
import logging
import platform
from datetime import timedelta

import psutil
from django.db import connection
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.shared.permissions import IsSuperAdmin, IsAdminStaff
from apps.shared.responses import success_response, error_response
from apps.dossiers.models import Dossier

logger = logging.getLogger('system')
User = get_user_model()


class HealthCheckView(APIView):
    """
    GET /api/system/health/
    Retourne l'état de santé du backend : DB, disque, mémoire, latence API.
    Accessible sans authentification (utilisé par Docker, Kubernetes, UptimeRobot, etc.).
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['System'],
        summary='Vérification de santé du système',
        description=(
            'Retourne le statut de connexion à la base de données, '
            'l\'espace disque disponible, la mémoire RAM, '
            'et la latence de réponse API.'
        ),
    )
    def get(self, request, *args, **kwargs):
        start_time = time.monotonic()

        # ── Database check ──
        db_status = 'ok'
        db_latency_ms = None
        try:
            db_start = time.monotonic()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            db_latency_ms = round((time.monotonic() - db_start) * 1000, 2)
        except Exception as e:
            db_status = f'error: {str(e)}'
            logger.error(f'[HealthCheck] Database connection failed: {e}')

        # ── Disk usage ──
        try:
            disk = psutil.disk_usage('/')
            disk_status = {
                'total_gb': round(disk.total / (1024 ** 3), 2),
                'used_gb': round(disk.used / (1024 ** 3), 2),
                'free_gb': round(disk.free / (1024 ** 3), 2),
                'percent_used': disk.percent,
            }
        except Exception as e:
            disk_status = {'error': str(e)}

        # ── Memory usage ──
        try:
            mem = psutil.virtual_memory()
            memory_status = {
                'total_gb': round(mem.total / (1024 ** 3), 2),
                'available_gb': round(mem.available / (1024 ** 3), 2),
                'percent_used': mem.percent,
            }
        except Exception as e:
            memory_status = {'error': str(e)}

        # ── CPU usage ──
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
        except Exception:
            cpu_percent = None

        # ── Cache check ──
        cache_status = 'ok'
        try:
            cache.set('_health_check', True, 10)
            if not cache.get('_health_check'):
                cache_status = 'error: could not read back'
        except Exception as e:
            cache_status = f'error: {str(e)}'

        # ── API latency ──
        api_latency_ms = round((time.monotonic() - start_time) * 1000, 2)

        # ── Overall status ──
        is_healthy = (
            db_status == 'ok'
            and cache_status == 'ok'
            and disk_status.get('percent_used', 100) < 95
            and memory_status.get('percent_used', 100) < 95
        )

        http_status = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response({
            'status': 'healthy' if is_healthy else 'unhealthy',
            'timestamp': timezone.now().isoformat(),
            'version': getattr(settings, 'APP_VERSION', '1.0.0'),
            'environment': 'production' if not settings.DEBUG else 'development',
            'checks': {
                'database': {
                    'status': db_status,
                    'latency_ms': db_latency_ms,
                },
                'cache': {
                    'status': cache_status,
                },
                'disk': disk_status,
                'memory': memory_status,
                'cpu_percent': cpu_percent,
            },
            'api_latency_ms': api_latency_ms,
        }, status=http_status)


class SystemMetricsView(APIView):
    """
    GET /api/system/metrics/
    Métriques avancées du système : nombre d'utilisateurs, dossiers,
    informations serveur. Réservé aux super_admins.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(
        tags=['System'],
        summary='Métriques système avancées',
        description='Informations détaillées sur le serveur, la base de données et les volumes.',
    )
    def get(self, request):
        # ── Cache des métriques (lourd en calcul) ──
        cache_key = 'system:metrics'
        cached = cache.get(cache_key)
        if cached:
            return success_response(data=cached)

        # ── Application metrics ──
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_citizens = User.objects.filter(role='citizen').count()
        total_agents = User.objects.exclude(role='citizen').count()
        total_dossiers = Dossier.objects.count()
        pending_dossiers = Dossier.objects.filter(
            status__in=[Dossier.Status.SUBMITTED, Dossier.Status.IN_REVIEW]
        ).count()

        # ── Dossiers created in last 24h / 7 days / 30 days ──
        now = timezone.now()
        dossiers_24h = Dossier.objects.filter(created_at__gte=now - timedelta(hours=24)).count()
        dossiers_7d = Dossier.objects.filter(created_at__gte=now - timedelta(days=7)).count()
        dossiers_30d = Dossier.objects.filter(created_at__gte=now - timedelta(days=30)).count()

        # ── Server info (sans exposer de données sensibles) ──
        server_info = {
            'os': platform.system(),
            'python_version': platform.python_version(),
            'architecture': platform.machine(),
            'django_debug': settings.DEBUG,
        }

        # ── Database info ──
        db_info = {}
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                row = cursor.fetchone()
                db_info['version'] = row[0] if row else 'unknown'
                cursor.execute(
                    "SELECT pg_size_pretty(pg_database_size(current_database()))"
                )
                row = cursor.fetchone()
                db_info['database_size'] = row[0] if row else 'unknown'
        except Exception as e:
            db_info['error'] = str(e)

        # ── Process info ──
        try:
            process = psutil.Process()
            process_info = {
                'pid': process.pid,
                'memory_mb': round(process.memory_info().rss / (1024 ** 2), 2),
                'cpu_percent': process.cpu_percent(),
                'threads': process.num_threads(),
                'uptime_seconds': round(time.time() - process.create_time()),
            }
        except Exception as e:
            process_info = {'error': str(e)}

        data = {
            'application': {
                'total_users': total_users,
                'active_users': active_users,
                'total_citizens': total_citizens,
                'total_agents': total_agents,
                'total_dossiers': total_dossiers,
                'pending_dossiers': pending_dossiers,
                'dossiers_last_24h': dossiers_24h,
                'dossiers_last_7d': dossiers_7d,
                'dossiers_last_30d': dossiers_30d,
            },
            'server': server_info,
            'database': db_info,
            'process': process_info,
        }

        # Cache 60 secondes (les métriques n'ont pas besoin d'être temps réel)
        cache.set(cache_key, data, 60)
        return success_response(data=data)


class SystemLogsView(APIView):
    """
    GET /api/system/logs/
    Lire les dernières lignes du fichier system.log. Réservé aux super_admins.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(
        tags=['System'],
        summary='Dernières entrées du journal système',
        parameters=[
            OpenApiParameter(
                name='lines',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Nombre de lignes à retourner (défaut: 50, max: 500).',
                required=False,
            ),
            OpenApiParameter(
                name='level',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filtrer par niveau de log (INFO, WARNING, ERROR).',
                required=False,
            ),
        ],
    )
    def get(self, request):
        try:
            num_lines = int(request.query_params.get('lines', 50))
            num_lines = min(max(num_lines, 1), 500)
        except (ValueError, TypeError):
            num_lines = 50

        level_filter = request.query_params.get('level', '').upper()
        valid_levels = {'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG'}

        log_file = settings.BASE_DIR / 'logs' / 'system.log'

        if not log_file.exists():
            return success_response(
                data={'lines': [], 'total_lines': 0, 'showing': 0},
                message='Aucun log disponible.',
            )

        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                all_lines = f.readlines()

            # Filtrage optionnel par niveau
            if level_filter and level_filter in valid_levels:
                filtered = [line for line in all_lines if level_filter in line]
            else:
                filtered = all_lines

            tail = filtered[-num_lines:]

            return success_response(data={
                'lines': [line.strip() for line in tail],
                'total_lines': len(all_lines),
                'showing': len(tail),
                'filter_applied': level_filter if level_filter in valid_levels else None,
            })
        except Exception as e:
            logger.error(f'[SystemLogs] Failed to read log file: {e}')
            return error_response(
                message='Erreur de lecture du fichier log.',
                status_code=500,
            )
