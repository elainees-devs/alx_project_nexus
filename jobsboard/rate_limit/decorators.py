# jobsboard/rate_limit/decorators.py
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .services import check_rate_limit, RateLimitExceeded

def rate_limit(action_name, limit, period_seconds):
    """
    Decorator for DRF views to enforce rate limits.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(viewset, request, *args, **kwargs):
            try:
                check_rate_limit(request.user, action_name, limit, period_seconds)
            except RateLimitExceeded as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            return func(viewset, request, *args, **kwargs)
        return wrapper
    return decorator
