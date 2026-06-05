"""
Intégrations mocks — Base abstraite pour tous les mocks.
"""
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('system')

class BaseMockClient(ABC):
    """
    Classe de base pour toutes les intégrations (Mocks).
    Garantit une interface standardisée pour les appels externes.
    """
    
    def __init__(self, service_name):
        self.service_name = service_name
        self.logger = logger
        
    def log_call(self, endpoint, payload):
        self.logger.info(f"[{self.service_name} Mock] Appel sur {endpoint} avec {payload}")
        
    @abstractmethod
    def ping(self):
        """Vérifie si le service est disponible."""
        pass
