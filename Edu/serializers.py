from rest_framework import serializers
from validators import uuid

from .models import *

class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formation
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'payment_type', 'amount', 'status', 'payment_method')
        read_only_fields = ('status', 'transaction_id')

    def create(self, validated_data):
        # Générer un ID de transaction unique
        validated_data['transaction_id'] = f"TRX-{uuid.uuid4().hex[:12].upper()}"
        return super().create(validated_data)

class InscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscription
        fields = ('id', 'amount_paid', 'payment_status', 'is_validated',
                 'sponsor_code_used')
        read_only_fields = ('payment_status', 'is_validated')

class TelegramSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramSubscription
        fields = ('id', 'subscription_date', 'is_active')
        read_only_fields = ('subscription_date',)