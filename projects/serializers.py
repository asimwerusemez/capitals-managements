from rest_framework import serializers
from django.contrib.auth import get_user_model

from accounts.serializers import CustomUserSerializer
from .models import (
    ProjectJoinRequest, Role, 
    ProjectModificationHistory, CustomNotification, 
    ProjectFinancement, ProjectInverstors, UsefulElementsForProject
)

User = get_user_model()

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions']


class ProjectModificationHistorySerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ProjectModificationHistory
        fields = ['project', 'project_name', 'user', 'user_name', 'field', 'old_value', 'new_value', 'timestamp', 'modification_type']


class CustomNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomNotification
        fields = ['id', 'user', 'message', 'created_at', 'read']

class ProjectInverstorsSerialiazer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    class Meta:
        model = ProjectInverstors
        fields = ["id", "project", "user", "is_admin", "status"]


class UsefulElementsForProjectSerialiazer(serializers.ModelSerializer):
    class Meta:
        model = UsefulElementsForProject
        fields =["id", "project", "name", "price", "acquired", "created_at", "update_at"]

class ProjectFinancementSerialiazer(serializers.ModelSerializer):
    investors = ProjectInverstorsSerialiazer(many=True, read_only=True)
    class Meta:
        model = ProjectFinancement
        fields =["id", "creator", "name", "description", "capital", "created_at", "update_at", "investors"]

class NotificationsSerialisers(serializers.ModelSerializer):
    class Meta:
        model = CustomNotification
        fields = "__all__"


class InvestorPaymentSerializer(serializers.Serializer):
    investor = serializers.CharField()
    total_payments = serializers.DecimalField(max_digits=10, decimal_places=2)

class ProjectPaymentSerializer(serializers.Serializer):
    project = serializers.CharField()
    investor_payments = serializers.ListField(
        child=InvestorPaymentSerializer()
    )

class ProjectInvestorSerializer(serializers.Serializer):
    project = serializers.CharField()
    investors = serializers.ListField(
        child=serializers.CharField()
    )

# class RecentActivitySerializer(serializers.ModelSerializer):
#     user = CustomUserSerializer(source='user.id', required=True)
#     project = serializers.CharField(source='project.name', required=True)
#     timestamp = serializers.DateTimeField(required=True)
#     class Meta:
#         model = ProjectModificationHistory
#         fields = ['project', 'user', 'field', 'old_value', 'new_value', 'timestamp', 'modification_type']

class DashboardSerializer(serializers.Serializer):
    total_projects = serializers.IntegerField()
    total_investors = serializers.IntegerField()
    total_payments = serializers.DecimalField(max_digits=10, decimal_places=2)
    investor_payments = ProjectPaymentSerializer(many=True)
    project_investors = ProjectInvestorSerializer(many=True)
    unread_notifications = serializers.IntegerField()
    recent_modifications = ProjectModificationHistorySerializer(many=True, required=False)

class ProjectDetailSerializer(serializers.Serializer):
    project_name = serializers.CharField()
    total_investors = serializers.IntegerField()
    total_payments = serializers.DecimalField(max_digits=10, decimal_places=2)
    investor_payments = serializers.ListField(
        child=serializers.DictField()
    )
    project_investors = serializers.ListField(
        child=serializers.CharField()
    )
    recent_modifications = serializers.ListField(
        child=serializers.DictField()
    )

class ProjectNameSerializer(serializers.Serializer):
    project_names = serializers.ListField(
        child=serializers.CharField()
    )
        


class ProjectJoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectJoinRequest
        fields = '__all__'