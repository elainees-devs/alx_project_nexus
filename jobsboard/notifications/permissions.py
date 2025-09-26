#jobsboard/notifications/permissions.py
from rest_framework import permissions

class NotificationPermission(permissions.BasePermission):
    """
    Admin and Employer can create/update/delete notifications.
    Job seekers can only read.
    """

    def has_permission(self, request, view):
        # Safe methods: allow all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Non-safe: only admin or employer
        return (
            request.user.is_authenticated and (
                request.user.is_staff or getattr(request.user, "role", None) == "employer"
            )
        )