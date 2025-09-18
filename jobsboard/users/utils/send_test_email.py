#jobsboard/users/utils/send_test_email
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_test_email():
    subject = "Test Email from JobBoard"
    message = "Hello! This is a test email sent from your Django app."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ["emuhombe@gmail.com"]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print(f"Email sent to {recipient_list}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        print(f"Failed to send email: {e}")
