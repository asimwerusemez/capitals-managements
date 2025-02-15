from django.db import models
from projects.models import ProjectFinancement, ProjectInverstors

class Payments(models.Model):
    project = models.ForeignKey(ProjectFinancement, on_delete=models.CASCADE)
    contributor = models.ForeignKey(ProjectInverstors, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)  # Correction : update_at devrait être auto_now=True
    received_by_admin = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"contribution de {self.contributor.user.username} de : ( ${self.amount} )"
