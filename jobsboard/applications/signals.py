# applications/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Application
from .tasks import send_reviewed_email_task


@receiver(pre_save, sender=Application)
def track_old_status(sender, instance, **kwargs):
    """
    Before saving, track the old status of the Application.
    This allows us to detect status changes in post_save.
    """
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
    """
    After saving, trigger an email if the application status changes to 'reviewed'.
    Uses Celery to send email asynchronously.
    """
    # Skip on creation
    if created:
        return

    old_status = getattr(instance, "_old_status", None)
    if instance.status == "reviewed" and old_status != "reviewed":
        # Ensure applicant has an email before queuing the task
        if instance.applicant and instance.applicant.email:
            send_reviewed_email_task.delay(
                username=instance.applicant.username,
                job_title=instance.job.title,
                email=instance.applicant.email,
            )
