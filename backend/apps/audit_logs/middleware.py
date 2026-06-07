import logging
from typing import Callable
from django.http import HttpRequest, HttpResponse

from .models import AuditLog

logger = logging.getLogger('errors')

class AuditMiddleware:
    """
    Middleware d'audit pour tracer toutes les requêtes de modification.
    Enregistre les opérations POST, PUT, PATCH, DELETE en base de données.
    """
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Exécution de la vue
        response = self.get_response(request)
        
        # On ne trace que les requêtes modifiantes
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self._log_action(request, response.status_code)
            
        return response

    def _log_action(self, request: HttpRequest, status_code: int) -> None:
        try:
            # Récupération sécurisée de l'IP, même derrière un Proxy/Nginx
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

            # Création de la trace en base de données
            AuditLog.objects.create(
                user=user,
                action=request.method,
                resource_type='API Request',
                details={
                    'path': request.path,
                    'status_code': status_code,
                    'method': request.method
                },
                ip_address=ip_address
            )
        except Exception as e:
            # Sécurité critique : On n'empêche JAMAIS l'utilisateur de recevoir sa réponse 
            # HTTP si le module d'audit tombe en panne.
            logger.error(f"Erreur AuditLog Middleware: {str(e)}", exc_info=True)
