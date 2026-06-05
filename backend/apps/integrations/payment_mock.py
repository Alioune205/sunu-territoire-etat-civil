import time
import uuid
import logging

logger = logging.getLogger('system')

class PaymentGatewayMock:
    """
    Mock client for Payment Gateways (Wave, Orange Money, Free Money).
    Simulates API calls for transaction initiation and status checking.
    """
    
    @staticmethod
    def initiate_payment(amount, phone_number, provider='wave'):
        """
        Simulates initiating a mobile money payment.
        """
        logger.info(f"[Payment Mock] Initiating {provider} payment of {amount} for {phone_number}")
        time.sleep(1) # Simulate network delay
        
        transaction_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "payment_url": f"https://mock-payment-gateway.local/pay/{transaction_id}",
            "status": "pending"
        }

    @staticmethod
    def check_transaction_status(transaction_id):
        """
        Simulates checking the status of a transaction.
        """
        logger.info(f"[Payment Mock] Checking status for transaction {transaction_id}")
        time.sleep(0.5)
        
        return {
            "transaction_id": transaction_id,
            "status": "completed", # Mocking that it's always successful
            "receipt_number": f"RCPT-{str(uuid.uuid4())[:8].upper()}"
        }
