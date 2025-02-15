from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, filters, permissions
from django.http import HttpResponse
import csv

from .models import ProjectJoinRequest, ProjectFinancement, ProjectInverstors, ProjectModificationHistory, UsefulElementsForProject, CustomNotification
from .serializers import ProjectJoinRequestSerializer, ProjectFinancementSerialiazer, ProjectInverstorsSerialiazer, ProjectModificationHistorySerializer, UsefulElementsForProjectSerialiazer, NotificationsSerialisers

import logging
logger = logging.getLogger(__name__)

class NotificationsViewSet(viewsets.ModelViewSet):
    queryset = CustomNotification.objects.all()
    serializer_class = NotificationsSerialisers
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CustomNotification.objects.filter(user=user)

class ProjectFinancementViewSet(viewsets.ModelViewSet):
    queryset = ProjectFinancement.objects.all()
    serializer_class = ProjectFinancementSerialiazer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        project = serializer.save(creator=self.request.user)
        ProjectInverstors.objects.create(project=project, user=self.request.user, is_admin=True, status='accepted')

    def get_queryset(self):
        user = self.request.user
        logger.info(f"User: {user}")
        projects = ProjectFinancement.objects.filter(investors__user=user)
        logger.info(f"Projects: {projects}")
        return projects

    def perform_destroy(self, instance):
        if instance.creator == self.request.user:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'status': 'only admin can delete projects'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.creator == self.request.user:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response({'status': 'only admin can update projects'}, status=status.HTTP_403_FORBIDDEN)

class UsefulElementsForProjectViewSet(viewsets.ModelViewSet):
    queryset = UsefulElementsForProject.objects.all()
    serializer_class = UsefulElementsForProjectSerialiazer

class ProjectInverstorsViewSet(viewsets.ModelViewSet):
    queryset = ProjectInverstors.objects.all()
    serializer_class = ProjectInverstorsSerialiazer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username']
    ordering_fields = ['user__username', 'is_admin']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ProjectInverstors.objects.filter(project__investors__user=user)

    def create(self, request, *args, **kwargs):
        user = request.user
        project = ProjectFinancement.objects.get(pk=request.data['project'])
        if not ProjectInverstors.objects.filter(project=project, user=user, is_admin=True).exists():
            return Response({"detail": "Only project admins can add investors."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def accept_invitation(self, request, pk=None):
        user = request.user
        invitation = self.get_object()
        if invitation.user != user:
            return Response({"detail": "You are not authorized to accept this invitation."}, status=status.HTTP_403_FORBIDDEN)
        invitation.status = 'accepted'
        invitation.save()
        return Response({"detail": "Invitation accepted."})

    @action(detail=True, methods=['post'])
    def reject_invitation(self, request, pk=None):
        user = request.user
        invitation = self.get_object()
        if invitation.user != user:
            return Response({"detail": "You are not authorized to reject this invitation."}, status=status.HTTP_403_FORBIDDEN)
        invitation.status = 'rejected'
        invitation.save()
        return Response({"detail": "Invitation rejected."})

class ProjectJoinRequestViewSet(viewsets.ModelViewSet):
    queryset = ProjectJoinRequest.objects.all()
    serializer_class = ProjectJoinRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ProjectJoinRequest.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def request_to_join(self, request, pk=None):
        user = request.user
        project = ProjectFinancement.objects.get(pk=pk)
        if ProjectJoinRequest.objects.filter(user=user, project=project).exists():
            return Response({"detail": "You have already requested to join this project."}, status=status.HTTP_400_BAD_REQUEST)
        join_request = ProjectJoinRequest.objects.create(user=user, project=project, status='pending')
        return Response({"detail": "Request to join project has been submitted."})

    @action(detail=True, methods=['post'])
    def accept_request(self, request, pk=None):
        user = request.user
        join_request = self.get_object()
        project = join_request.project
        if not ProjectInverstors.objects.filter(project=project, user=user, is_admin=True).exists():
            return Response({"detail": "Only project admins can accept join requests."}, status=status.HTTP_403_FORBIDDEN)
        join_request.status = 'accepted'
        ProjectInverstors.objects.create(user=join_request.user, project=project, is_admin=False)
        join_request.save()
        return Response({"detail": "Request accepted."})

    @action(detail=True, methods=['post'])
    def reject_request(self, request, pk=None):
        user = request.user
        join_request = self.get_object()
        project = join_request.project
        if not ProjectInverstors.objects.filter(project=project, user=user, is_admin=True).exists():
            return Response({"detail": "Only project admins can reject join requests."}, status=status.HTTP_403_FORBIDDEN)
        join_request.status = 'rejected'
        join_request.save()
        return Response({"detail": "Request rejected."})

class DataExportView(viewsets.ViewSet):
    def export_projects(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="projects.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Description', 'Capital', 'Creator'])

        projects = ProjectFinancement.objects.all()
        for project in projects:
            writer.writerow([project.id, project.name, project.description, project.capital, project.creator.username])

        return response

    def export_investors(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="investors.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Project', 'User', 'Is Admin'])

        investors = ProjectInverstors.objects.all()
        for investor in investors:
            writer.writerow([investor.id, investor.project.name, investor.user.username, investor.is_admin])

        return response



class ProjectModificationHistoryViewSet(viewsets.ModelViewSet):
    queryset = ProjectModificationHistory.objects.all()
    serializer_class = ProjectModificationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        projects_as_investor = ProjectInverstors.objects.filter(user=user).values_list('project', flat=True)
        return ProjectModificationHistory.objects.filter(project__in=projects_as_investor).order_by('-timestamp')
