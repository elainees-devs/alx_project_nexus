# jobsboard/applications/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Application
from .tasks import send_reviewed_email_task


@receiver(pre_save, sender=Application)
def track_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Application.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Application.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Application)
def trigger_reviewed_email(sender, instance, created, **kwargs):
    if created:
        return

    if instance.status == "reviewed" and getattr(instance, "_old_status", None) != "reviewed":
        # Queue email via Celery 
        send_reviewed_email_task.delay(
            instance.applicant.username,
            instance.job.title,
            instance.applicant.email,
        )
