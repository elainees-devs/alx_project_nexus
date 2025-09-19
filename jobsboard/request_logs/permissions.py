# jobsboard/request_logs/permissions.py
from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission:
    - Admins can see all logs
    - Regular users can see only their own logs
    """

    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.is_superuser:
            return True
        # Users can access only their own log
        return obj.user == request.user
