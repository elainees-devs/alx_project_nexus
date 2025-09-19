#jobsboard/rate_limit/services.py
from django.utils import timezone
from django.db import transaction
from .models import RateLimit, RateLimitAction
from request_logs.models import RequestLog

class RateLimitExceeded(Exception):
    """Raised when a user exceeds the allowed rate limit."""
    def __init__(self, wait_time, request=None):
        self.wait_time = wait_time
        self.request = request
        super().__init__(f"Rate limit exceeded. Try again in {wait_time} seconds.")


def check_rate_limit(user, action_name, limit: int, period_seconds: int, request=None):
    """
    Checks and updates the rate limit for a user and action.
    Returns True if allowed, raises RateLimitExceeded if exceeded.
    Logs a request if the limit is exceeded.
    """
    action, _ = RateLimitAction.objects.get_or_create(name=action_name)
    now = timezone.now()

    # Start a transaction to avoid race conditions
    with transaction.atomic():
        rate, created = RateLimit.objects.select_for_update().get_or_create(
            user=user,
            action=action,
            period_start__lte=now,
            defaults={"count": 0, "period_seconds": period_seconds, "period_start": now}
        )

        # Reset period if expired
        period_end = rate.period_start + timezone.timedelta(seconds=rate.period_seconds)
        if now >= period_end:
            rate.count = 0
            rate.period_start = now
            rate.period_seconds = period_seconds

        if rate.count >= limit:
            remaining = (rate.period_start + timezone.timedelta(seconds=period_seconds) - now).total_seconds()
            
            # Log the rate-limit hit
            if request:
                ip = request.META.get("REMOTE_ADDR", "unknown")
                RequestLog.objects.create(
                    user=user,
                    ip_address=ip,
                    endpoint=request.path,
                    method=request.method,
                    status_code=429  # Too Many Requests
                )
            
            raise RateLimitExceeded(int(remaining), request=request)

        rate.count += 1
        rate.save()

    return True

def check_failed_login(user, request=None):
    """
    Limit failed login attempts to 5 in 15 minutes.
    Raises RateLimitExceeded if exceeded.
    """
    return check_rate_limit(
        user=user,
        action_name="failed_login",
        limit=5,
        period_seconds=15 * 60,  # 15 minutes
        request=request
    )

