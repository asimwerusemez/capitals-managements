from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from payments.models import Payments
from .models import ProjectFinancement, ProjectModificationHistory
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(pre_save, sender=ProjectFinancement)
def log_project_pre_save(sender, instance, **kwargs):
    if instance.pk:  # If instance already exists (update)
        old_instance = sender.objects.get(pk=instance.pk)
        instance._pre_save_instance = old_instance

@receiver(post_save, sender=ProjectFinancement)
def log_project_modification(sender, instance, created, **kwargs):
    if created:
        modification_type = "creation"
        old_value = None
        new_value = instance.name
    else:
        modification_type = "update"
        old_value = instance._pre_save_instance.name if hasattr(instance, '_pre_save_instance') else None
        new_value = instance.name

    ProjectModificationHistory.objects.create(
        project=instance,
        user=instance.creator,
        field='name',
        old_value=old_value,
        new_value=new_value,
        modification_type=modification_type,
    )

@receiver(post_delete, sender=ProjectFinancement)
def log_project_deletion(sender, instance, **kwargs):
    ProjectModificationHistory.objects.create(
        project=instance,
        user=instance.creator,
        field='name',
        old_value=instance.name,
        new_value=None,
        modification_type='deletion',
    )

@receiver(post_save, sender=Payments)
def log_payment_modification(sender, instance, created, **kwargs):
    modification_type = "payment_creation" if created else "payment_update"
    ProjectModificationHistory.objects.create(
        project=instance.project,
        user=instance.contributor.user,
        field='amount',
        old_value=None,
        new_value=str(instance.amount),
        modification_type=modification_type,
    )
