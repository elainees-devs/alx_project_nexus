# jobsboard/applications/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_reviewed_email_task(username, job_title, email):
    """
    Task to send an email when application status is reviewed.
    """
    subject = f"Your application for {job_title} has been reviewed"
    message = (
        f"Hello {username},\n\n"
        f"Your application for '{job_title}' has been reviewed by the recruiter.\n"
        "You will be contacted if you are shortlisted.\n\n"
        "Thank you for applying!"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
