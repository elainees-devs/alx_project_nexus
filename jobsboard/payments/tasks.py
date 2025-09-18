# jobsboard/payments/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_payment_confirmation_email(user_email, amount, payment_type):
    send_mail(
        subject=f"Payment Confirmation: {payment_type}",
        message=f"Your payment of {amount} has been successfully processed.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
