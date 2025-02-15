from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, filters
from django.http import HttpResponse
import csv

from projects.models import CustomNotification
from .models import (
    Payments
)

from .serializers import PaymentsSerializer


class PaymentsViewSet(viewsets.ModelViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializer

    def get_queryset(self):
        user = self.request.user
        return Payments.objects.filter(contributor__user=user)

    def perform_create(self, serializer):
        payment = serializer.save()
        # Envoyer une notification à l'admin
        admin = payment.project.creator
        CustomNotification.objects.create(
            user=admin, 
            title="Nouvelle contribution",
            body=f"Nouvelle contribution de {payment.contributor.user.username} de : ${payment.amount}"
        )

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        payment = self.get_object()
        if payment.project.creator == request.user:
            payment.received_by_admin = True
            payment.save()
            return Response({'status': 'payment confirmed'})
        return Response({'status': 'only admin can confirm payments'}, status=status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        if instance.project.creator == self.request.user:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'status': 'only admin can delete payments'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.project.creator == self.request.user:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response({'status': 'only admin can update payments'}, status=status.HTTP_403_FORBIDDEN)




# exportation des donnees sous format csv
class DataPaymentsExportView(viewsets.ViewSet):
    def export_payments(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payments.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Project', 'Contributor', 'Amount', 'Received By Admin'])

        payments = Payments.objects.all()
        for payment in payments:
            writer.writerow([payment.id, payment.project.name, payment.contributor.user.username, payment.amount, payment.received_by_admin])

        return response


