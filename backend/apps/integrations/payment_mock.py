"""
Mock pour les passerelles de paiement.
"""
import time
import uuid
from .base import BaseMockClient

class PaymentGatewayMock(BaseMockClient):
    """
    Client de simulation pour Wave/Orange Money/Free Money.
    """
    def __init__(self):
        super().__init__("PAYMENT")
        
    def ping(self):
        return {"status": "up"}

    def initiate_payment(self, amount, phone_number, provider='wave'):
        self.log_call("initiate_payment", {
            "amount": amount, "phone": phone_number, "provider": provider
        })
        time.sleep(0.8)
        
        transaction_id = str(uuid.uuid4())
        return {
            "success": True,
            "transaction_id": transaction_id,
            "payment_url": f"https://mock-payment.local/pay/{transaction_id}",
            "status": "pending"
        }

    def check_transaction_status(self, transaction_id):
        self.log_call("check_status", {"transaction_id": transaction_id})
        time.sleep(0.3)
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "status": "completed",
            "receipt_number": f"RCPT-{str(uuid.uuid4())[:8].upper()}"
        }
