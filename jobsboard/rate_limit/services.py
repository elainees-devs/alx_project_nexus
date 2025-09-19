# jobsboard/rate_limit/services.py
from django.utils import timezone
from .models import RateLimit, RateLimitAction
from django.db import transaction

class RateLimitExceeded(Exception):
    """Raised when a user exceeds the allowed rate limit."""
    def __init__(self, wait_time):
        self.wait_time = wait_time
        super().__init__(f"Rate limit exceeded. Try again in {wait_time} seconds.")


def check_rate_limit(user, action_name, limit: int, period_seconds: int):
    """
    Checks and updates the rate limit for a user and action.
    Returns True if allowed, raises RateLimitExceeded if exceeded.
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
            raise RateLimitExceeded(int(remaining))

        rate.count += 1
        rate.save()

    return True
