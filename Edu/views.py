# Edu/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Formation, Inscription, Payment, TelegramSubscription
from .serializers import (FormationSerializer, PaymentSerializer,
                          InscriptionSerializer, TelegramSubscriptionSerializer)
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.conf import settings
import hmac
import hashlib

class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        # Ici, vous feriez l'intégration avec votre API de paiement
        # et mettriez à jour le statut en fonction de la réponse

    @action(detail=True, methods=['POST'])
    def confirm_payment(self, request, pk=None):
        payment = self.get_object()
        # Logique de confirmation de paiement
        if payment.payment_type == 'inscription':
            user = request.user
            user.is_paid = True
            user.save()

            # Calculer et distribuer les commissions
            sponsorship = user.sponsored_by.first()
            if sponsorship:
                sponsor = sponsorship.sponsor
                commission = payment.amount * (sponsorship.commission_percentage / 100)
                sponsor.wallet_balance += commission
                sponsor.save()

        return Response({'status': 'payment confirmed'})





class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]  # Les webhooks doivent être accessibles sans auth

    def verify_signature(self, request):
        """Vérifie la signature du webhook"""
        received_signature = request.headers.get('X-Payment-Signature')
        if not received_signature:
            return False

        # Calculer la signature avec votre clé secrète
        payload = request.body
        secret = settings.PAYMENT_WEBHOOK_SECRET
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(received_signature, expected_signature)

    def post(self, request):
        # Vérifier la signature
        if not self.verify_signature(request):
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Traiter la notification
        payment_data = request.data
        transaction_id = payment_data.get('transaction_id')

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)

            if payment_data['status'] == 'success':
                payment.status = 'completed'
                payment.save()

                # Mettre à jour le statut de l'utilisateur si c'est un paiement d'inscription
                if payment.payment_type == 'inscription':
                    user = payment.user
                    user.is_paid = True
                    user.save()

                    # Traiter les commissions de parrainage
                    sponsorship = user.sponsored_by.first()
                    if sponsorship:
                        sponsor = sponsorship.sponsor
                        commission = payment.amount * (sponsorship.commission_percentage / 100)
                        sponsor.wallet_balance += commission
                        sponsor.save()

            elif payment_data['status'] == 'failed':
                payment.status = 'failed'
                payment.save()

            return Response({'status': 'processed'})

        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )