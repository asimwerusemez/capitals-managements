from django.urls import path, include
from rest_framework.routers import DefaultRouter

from projects.dashboard import DashboardViewSet
from .views import (
    ProjectFinancementViewSet, ProjectInverstorsViewSet, 
    UsefulElementsForProjectViewSet, NotificationsViewSet, 
    ProjectJoinRequestViewSet, ProjectModificationHistoryViewSet, 
    DataExportView
)

router = DefaultRouter()
router.register(r'projects', ProjectFinancementViewSet, basename='project')
router.register(r'inverstors', ProjectInverstorsViewSet, basename='inverstors')
router.register(r'useful-elements', UsefulElementsForProjectViewSet, basename='useful-elements')
router.register(r'notifications', NotificationsViewSet, basename='notification')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'join-requests', ProjectJoinRequestViewSet, basename='join-requests')
router.register(r'modification-history', ProjectModificationHistoryViewSet, basename='modification-history')

urlpatterns = [
    path('api/', include(router.urls)),
    path('export/projects/', DataExportView.as_view({'get': 'export_projects'})),
    path('export/investors/', DataExportView.as_view({'get': 'export_investors'})),
]
