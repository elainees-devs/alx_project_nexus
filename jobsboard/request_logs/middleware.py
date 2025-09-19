#jobsboard/request_logs/middleware.py
from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log every HTTP request and response.
    """

    def process_response(self, request, response):
        # Skip admin or static requests if needed
        if request.path.startswith("/admin") or request.path.startswith("/static"):
            return response

        # Get client IP
        ip_address = self.get_client_ip(request)

        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None

        # Create the log
        RequestLog.objects.create(
            user=user,
            ip_address=ip_address,
            endpoint=request.path,
            method=request.method,
            status_code=response.status_code
        )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
