"""
Mock pour l'Agence Nationale de l'Etat Civil (ANEC).
"""
import time
from .base import BaseMockClient

class ANECMockClient(BaseMockClient):
    """
    Client de simulation pour l'ANEC.
    """
    def __init__(self):
        super().__init__("ANEC")
        
    def ping(self):
        return {"status": "up", "latency": "45ms"}

    def verify_cni(self, cni_number):
        self.log_call("verify_cni", {"cni_number": cni_number})
        time.sleep(0.5)
        
        if not cni_number or str(cni_number).startswith('0'):
            return {
                "success": False,
                "error": "CNI invalide ou introuvable",
            }
            
        return {
            "success": True,
            "data": {
                "cni_number": cni_number,
                "first_name": "Jean",
                "last_name": "Dupont",
                "date_of_birth": "1980-05-14",
                "place_of_birth": "Dakar",
                "is_active": True
            }
        }
