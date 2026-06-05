import psutil
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

class HealthCheckView(APIView):
    """
    Returns the health status of the backend.
    """
    permission_classes = [AllowAny]

    @extend_schema(tags=['System'], summary="Check system health")
    def get(self, request, *args, **kwargs):
        # Check DB connection
        db_status = "ok"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Disk usage
        disk_usage = psutil.disk_usage('/')
        disk_status = {
            "total": disk_usage.total,
            "used": disk_usage.used,
            "free": disk_usage.free,
            "percent": disk_usage.percent
        }
        
        return Response({
            "status": "healthy" if db_status == "ok" else "unhealthy",
            "database": db_status,
            "disk": disk_status,
        })
