#jobsboard/rate_limit/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

# ---------------------------------------------------------
# RateLimitAction Model
# ---------------------------------------------------------
# Represents an action that can be rate-limited.
# - Examples: "create_job", "send_message", "login_attempt".
# - Ensures uniqueness per action name for consistent rate-limiting.
class RateLimitAction(models.Model):
    """
    Defines a specific action that can be rate-limited.
    Example: "create_job", "send_message", "login_attempt"
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# ---------------------------------------------------------
# RateLimit Model
# ---------------------------------------------------------
# Tracks the number of requests a user performs for a specific action within a defined time period.
# - Each record tracks: user, action, count, period start, and period duration in seconds.
# - Enforces uniqueness per (user, action, period_start) to prevent duplicate tracking.
# - Indexed on user and action for efficient query performance.
class RateLimit(models.Model):
    """
    Tracks requests per user + action within a period.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rate_limits"
    )
    action = models.ForeignKey(
        RateLimitAction, on_delete=models.CASCADE, related_name="limits"
    )
    count = models.IntegerField(default=0)
    period_start = models.DateTimeField(default=timezone.now)
    period_seconds = models.IntegerField()

    class Meta:
        unique_together = ("user", "action", "period_start")
        indexes = [
            models.Index(fields=['user', 'action'], name='idx_rate_limits_user_action'),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} ({self.count})"


