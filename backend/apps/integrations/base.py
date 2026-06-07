"""
Base class for system integrations.
"""
from abc import ABC, abstractmethod


class BaseIntegrationService(ABC):
    """
    Abstract Base Class outlining the integration API structure for external services.
    """

    def __init__(self, api_url=None, api_key=None):
        self.api_url = api_url
        self.api_key = api_key

    @abstractmethod
    def authenticate(self):
        """
        Authenticates with the external API endpoint.
        Should raise connection/auth errors on failure.
        """
        pass

    @abstractmethod
    def fetch_citizen_data(self, cni_number):
        """
        Fetches official identity information using a National CNI number.
        """
        pass

    @abstractmethod
    def verify_civil_status_record(self, record_id, record_type):
        """
        Verifies the authenticity of a birth/marriage/death certificate record.
        """
        pass

    @abstractmethod
    def transmit_dossier(self, dossier_data):
        """
        Transmits completed dossier details to government archival vaults.
        """
        pass
