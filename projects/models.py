from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectFinancement(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    capital = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"creation de projet: {self.name} par : {self.creator.username}"

class ProjectInverstors(models.Model):
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    project = models.ForeignKey(ProjectFinancement, on_delete=models.CASCADE, related_name="investors")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='invited')

    def __str__(self):
        return f"{self.user.username} investisseur dans le projet: {self.project.name}"


class ProjectJoinRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    project = models.ForeignKey(ProjectFinancement, on_delete=models.CASCADE, related_name="join_requests")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} demande à rejoindre le projet: {self.project.name}"

class UsefulElementsForProject(models.Model):
    project = models.ForeignKey(ProjectFinancement, on_delete=models.CASCADE, related_name="elements")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    aquired = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ajout de l'element: {self.name} qui coute : ${self.price}"

class CustomNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.body

class Role(models.Model):
    name = models.CharField(max_length=50)
    permissions = models.TextField()

    def __str__(self):
        return self.name
    

class ProjectModificationHistory(models.Model):
    project = models.ForeignKey(ProjectFinancement, on_delete=models.CASCADE, related_name="modification_history")
    user = models.ForeignKey(User, related_name="modifications", on_delete=models.CASCADE)
    field = models.CharField(max_length=50)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    modification_type = models.CharField(max_length=50)

    def __str__(self):
        return f"Modification de {self.field} par {self.user.username} le {self.timestamp}"


