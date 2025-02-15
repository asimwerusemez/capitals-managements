from django.contrib import admin
from .models import (
    ProjectFinancement, ProjectInverstors, 
    UsefulElementsForProject, CustomNotification,
    ProjectJoinRequest, ProjectModificationHistory
)


admin.site.register(ProjectFinancement)
admin.site.register(ProjectInverstors)
admin.site.register(UsefulElementsForProject)
admin.site.register(CustomNotification)
admin.site.register(ProjectJoinRequest)
admin.site.register(ProjectModificationHistory)
