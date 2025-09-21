#jobsboard/analytics/permissions.py
from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Allows access only to superusers/admins.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsEmployerUser(BasePermission):
    """
    Allows access only to employers (who created the job).
    """
    def has_permission(self, request, view):
        return request.user and getattr(request.user, 'role', None) == 'employer'
