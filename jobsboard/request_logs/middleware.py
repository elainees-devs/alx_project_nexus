# jobsboard/request_logs/middleware.py
from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Logs every authenticated user's request, except request_logs endpoints.
    """
    def process_response(self, request, response):
        try:
            if hasattr(request, "user") and request.user.is_authenticated:
                if not request.path.startswith("/api/request-logs/"):
                    RequestLog.objects.create(
                        user=request.user,
                        ip_address=request.META.get("REMOTE_ADDR", "127.0.0.1"),
                        endpoint=request.path,
                        method=request.method,
                        status_code=response.status_code,
                    )
        except Exception as e:
            # Don't break tests if logging fails
            print(f"Logging middleware error: {e}")
        return response
