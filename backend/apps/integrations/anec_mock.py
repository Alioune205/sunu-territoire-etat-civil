import time
import logging

logger = logging.getLogger('system')

class ANECMockClient:
    """
    Mock client for the Agence Nationale de l'Etat Civil (ANEC).
    Simulates API calls to the national registry.
    """
    
    @staticmethod
    def verify_cni(cni_number):
        """
        Simulates verification of a National Identity Card number.
        Returns a mock payload.
        """
        logger.info(f"[ANEC Mock] Verifying CNI: {cni_number}")
        time.sleep(1) # Simulate network delay
        
        # Simple mock logic: fail if CNI starts with 0
        if cni_number and str(cni_number).startswith('0'):
            return {
                "is_valid": False,
                "error": "CNI invalide ou non trouvée dans le registre national"
            }
            
        return {
            "is_valid": True,
            "data": {
                "cni_number": cni_number,
                "first_name": "Mock First Name",
                "last_name": "Mock Last Name",
                "date_of_birth": "1990-01-01",
                "place_of_birth": "Dakar",
                "status": "active"
            }
        }
