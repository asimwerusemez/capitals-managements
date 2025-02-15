from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from .models import CustomNotification
from payments.models import Payments
from .models import ProjectFinancement, ProjectInverstors, ProjectModificationHistory
from .serializers import DashboardSerializer, ProjectModificationHistorySerializer, ProjectDetailSerializer, ProjectNameSerializer

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        user = request.user

        # Total des projets pour l'utilisateur
        total_projects = ProjectFinancement.objects.filter(investors__user=user).count()

        # Total des investisseurs
        total_investors = ProjectInverstors.objects.filter(project__investors__user=user).values('user').distinct().count()

        # Projets où l'utilisateur est investisseur
        projects_as_investor = ProjectInverstors.objects.filter(user=user).values_list('project', flat=True)

        if not projects_as_investor:
            return Response({'error': 'No projects found.'}, status=status.HTTP_404_NOT_FOUND)

        # Prendre seulement le premier projet
        first_project_id = projects_as_investor[0]

        # Paiements pour le premier projet
        project_investor_payments = (Payments.objects
                                     .filter(project=first_project_id)
                                     .values('project__name', 'contributor__user__username')
                                     .annotate(total=Sum('amount')))

        # Agrégation des paiements par investisseur
        project_payments_data = []
        for payment in project_investor_payments:
            project_payments_data.append({
                'investor': payment['contributor__user__username'],
                'total_payments': payment['total']
            })

        # Investisseurs pour le premier projet
        project_investors = ProjectInverstors.objects.filter(project=first_project_id).values('user__username').distinct()
        project_investors_data = [investor['user__username'] for investor in project_investors]

        # Historique des modifications pour le premier projet
        recent_modifications = ProjectModificationHistory.objects.filter(project=first_project_id).select_related('user').order_by('-timestamp')[:5]
        recent_modifications_data = ProjectModificationHistorySerializer(recent_modifications, many=True).data

        data = {
            'project_name': ProjectFinancement.objects.get(id=first_project_id).name,
            'total_investors': len(project_investors_data),
            'total_payments': sum(payment['total_payments'] for payment in project_payments_data),
            'investor_payments': project_payments_data,
            'project_investors': project_investors_data,
            'recent_modifications': recent_modifications_data,
        }

        serializer = ProjectDetailSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def project_detail(self, request):
        project_name = request.data.get('project_name')

        if not project_name:
            return Response({'error': 'Project name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = ProjectFinancement.objects.get(name=project_name)
        except ProjectFinancement.DoesNotExist:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Paiements pour le projet spécifique
        investor_payments = (Payments.objects
                             .filter(project=project)
                             .values('contributor__user__username')
                             .annotate(total=Sum('amount')))

        investor_payments_data = []
        for payment in investor_payments:
            investor_payments_data.append({
                'investor': payment['contributor__user__username'],
                'total_payments': payment['total']
            })

        # Investisseurs pour le projet spécifique
        project_investors = ProjectInverstors.objects.filter(project=project).values('user__username').distinct()
        project_investors_data = [investor['user__username'] for investor in project_investors]

        # Historique des modifications pour le projet spécifique
        recent_modifications = ProjectModificationHistory.objects.filter(project=project).select_related('user').order_by('-timestamp')[:5]
        recent_modifications_data = ProjectModificationHistorySerializer(recent_modifications, many=True).data

        data = {
            'project_name': project.name,
            'total_investors': len(project_investors_data),
            'total_payments': sum(payment['total_payments'] for payment in investor_payments_data),
            'investor_payments': investor_payments_data,
            'project_investors': project_investors_data,
            'recent_modifications': recent_modifications_data,
        }

        serializer = ProjectDetailSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def project_names(self, request):
        user = request.user

        # Récupérer les projets où l'utilisateur est investisseur
        projects_as_investor = ProjectInverstors.objects.filter(user=user).values_list('project__name', flat=True).distinct()

        if not projects_as_investor:
            return Response({'error': 'No projects found.'}, status=status.HTTP_404_NOT_FOUND)

        data = {'project_names': list(projects_as_investor)}

        serializer = ProjectNameSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
