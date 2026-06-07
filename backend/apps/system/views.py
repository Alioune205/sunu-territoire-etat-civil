"""
Views for System Monitoring (Super Admin only).
"""
import os
import sys
import shutil
import platform
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.db import connection, models
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from apps.shared.permissions import IsSuperAdmin
from apps.shared.responses import success_response, error_response
from apps.audit_logs.models import AuditLog

import django

# Record process startup time
STARTUP_TIME = timezone.now()


class SystemHealthView(APIView):
    """
    GET /api/system/health/
    Retrieves system health status including CPU, memory, disk, DB connection, and uptime.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(
        tags=['System Monitoring'],
        summary='Obtenir l\'état de santé du système et des ressources',
    )
    def get(self, request):
        # 1. DB Health
        db_status = "healthy"
        db_response_time_ms = 0
        try:
            start_db = datetime.now()
            # Perform a simple raw query to check connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
            db_response_time_ms = round((datetime.now() - start_db).total_seconds() * 1000, 2)
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"

        # 2. Disk Usage
        try:
            total, used, free = shutil.disk_usage(settings.BASE_DIR)
            disk_total_gb = round(total / (1024**3), 2)
            disk_used_gb = round(used / (1024**3), 2)
            disk_free_gb = round(free / (1024**3), 2)
            disk_used_percent = round((used / total) * 100.0, 2)
        except Exception:
            disk_total_gb = disk_used_gb = disk_free_gb = disk_used_percent = None

        # 3. CPU & Memory Usage
        cpu_percent = None
        ram_total_gb = ram_used_gb = ram_free_gb = ram_percent = None
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            ram_total_gb = round(mem.total / (1024**3), 2)
            ram_used_gb = round(mem.used / (1024**3), 2)
            ram_free_gb = round(mem.available / (1024**3), 2)
            ram_percent = mem.percent
        except ImportError:
            pass

        # 4. Uptime & Platform Info
        uptime_seconds = int((timezone.now() - STARTUP_TIME).total_seconds())
        uptime_str = str(timedelta(seconds=uptime_seconds))

        data = {
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'timestamp': timezone.now(),
            'database': {
                'status': db_status,
                'response_time_ms': db_response_time_ms,
                'engine': connection.vendor
            },
            'resources': {
                'cpu_percent': cpu_percent,
                'ram': {
                    'total_gb': ram_total_gb,
                    'used_gb': ram_used_gb,
                    'free_gb': ram_free_gb,
                    'percent': ram_percent
                },
                'disk': {
                    'total_gb': disk_total_gb,
                    'used_gb': disk_used_gb,
                    'free_gb': disk_free_gb,
                    'percent': disk_used_percent
                }
            },
            'environment': {
                'python_version': sys.version.split()[0],
                'django_version': django.get_version(),
                'os': f"{platform.system()} {platform.release()}",
                'uptime': uptime_str,
                'uptime_seconds': uptime_seconds
            }
        }

        return success_response(data=data, message="Diagnostic système récupéré.")


class SystemLogsView(APIView):
    """
    GET /api/system/logs/
    Reads the backend application log file (Super Admin only).
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(
        tags=['System Monitoring'],
        summary='Consulter les fichiers de logs système',
        parameters=[
            OpenApiParameter('lines', OpenApiTypes.INT, description='Nombre de lignes à retourner', default=100),
            OpenApiParameter('level', OpenApiTypes.STR, description='Filtrer par niveau (INFO, WARNING, ERROR)'),
        ]
    )
    def get(self, request):
        # 1. Determine log file path from settings, or fall back to base logs folder
        log_dir = settings.BASE_DIR / 'logs'
        log_file_path = log_dir / 'app.log'

        # Check default paths if not exists
        if not log_file_path.exists():
            # Create the logs folder and file to prevent file-not-found crashes
            os.makedirs(log_dir, exist_ok=True)
            with open(log_file_path, 'w', encoding='utf-8') as f:
                f.write(f"[{timezone.now().isoformat()}] INFO system Log file initialized.\n")

        lines_to_read = request.query_params.get('lines', 100)
        try:
            lines_to_read = min(int(lines_to_read), 1000)  # cap at 1000 lines
        except ValueError:
            lines_to_read = 100

        level_filter = request.query_params.get('level')
        if level_filter:
            level_filter = level_filter.upper()

        log_lines = []
        try:
            # Read file in reverse order or read all and take last N lines
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Filter by level if specified
            if level_filter:
                lines = [line for line in lines if level_filter in line]

            # Slice last N lines
            lines = lines[-lines_to_read:]
            log_lines = [line.strip() for line in lines]
        except Exception as e:
            return error_response(message=f"Impossible de lire le fichier de logs: {str(e)}")

        data = {
            'log_file': str(log_file_path),
            'total_lines': len(log_lines),
            'lines': log_lines
        }
        return success_response(data=data, message="Logs récupérés avec succès.")


class SystemActivityView(APIView):
    """
    GET /api/system/activity/
    Aggregates AuditLog data to monitor backend actions and events.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(
        tags=['System Monitoring'],
        summary='Obtenir l\'analyse d\'activité système',
    )
    def get(self, request):
        logs = AuditLog.objects.all()

        # 1. General counts
        total_logs = logs.count()

        # 2. Action distribution
        action_counts = logs.values('action').annotate(count=Count('id')).order_by('-count')
        action_labels = dict(AuditLog.Action.choices)
        actions = [{
            'action': item['action'],
            'label': action_labels.get(item['action'], item['action']),
            'count': item['count']
        } for item in action_counts]

        # 3. Resource type distribution
        resource_counts = logs.values('resource_type').annotate(count=Count('id')).order_by('-count')[:10]
        resources = [{
            'resource_type': item['resource_type'],
            'count': item['count']
        } for item in resource_counts]

        # 4. Activity trends (Last 7 days)
        seven_days_ago = timezone.now().date() - timedelta(days=7)
        from django.db.models.functions import TruncDate
        trend_stats = logs.filter(created_at__date__gte=seven_days_ago)\
                          .annotate(date=TruncDate('created_at'))\
                          .values('date')\
                          .annotate(count=Count('id'))\
                          .order_by('date')
        trends = [{'date': item['date'], 'count': item['count']} for item in trend_stats if item['date']]

        # 5. Top active users
        user_stats = logs.values('user__id', 'user__email', 'user__first_name', 'user__last_name')\
                         .annotate(count=Count('id'))\
                         .order_by('-count')[:5]
        active_users = []
        for item in user_stats:
            if item['user__id']:
                name = f"{item['user__first_name']} {item['user__last_name']}".strip()
                active_users.append({
                    'user_id': item['user__id'],
                    'email': item['user__email'],
                    'name': name or item['user__email'],
                    'action_count': item['count']
                })

        data = {
            'total_actions': total_logs,
            'action_distribution': actions,
            'resource_distribution': resources,
            'weekly_trend': trends,
            'top_active_users': active_users
        }
        return success_response(data=data, message="Analyse d'activité système réussie.")
