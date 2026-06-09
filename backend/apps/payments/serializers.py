from rest_framework import serializers
from .models import PaymentTransaction, TreasuryTransfer

class TreasuryTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreasuryTransfer
        fields = ['id', 'transferred_at', 'transfer_reference', 'validated_by']

class PaymentTransactionSerializer(serializers.ModelSerializer):
    treasury_transfers = TreasuryTransferSerializer(many=True, read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'reference', 'amount', 'currency', 'payment_type',
            'status', 'payer_name', 'payer_id', 'service_label',
            'created_at', 'updated_at', 'treasury_transfers'
        ]
