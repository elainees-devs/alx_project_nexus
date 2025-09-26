from rest_framework import permissions
from users.models import User


class PaymentPermission(permissions.BasePermission):
    """
    Payment access rules:
    - Job Seekers, Employers, and Admins can initiate payments.
    - Users can list/retrieve only their own payments.
    - Verification is allowed for the owner or admin.
    - Updates and deletes are restricted to admins.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # ✅ Initiate: Seekers, Employers, Admins
        if view.action == "initiate":
            return user.role in [User.ROLE_SEEKER, User.ROLE_EMPLOYER, User.ROLE_ADMIN]

        # ✅ Verify: allowed for owner (checked later in object perms) or admin
        if view.action in ["verify", "verified"]:
            return True

        # ✅ Admin-only actions
        if view.action in ["update", "partial_update", "destroy"]:
            return user.role == User.ROLE_ADMIN

        # ✅ Listing & retrieving: all authenticated users
        if view.action in ["list", "retrieve", "create"]:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # ✅ Admins can always act
        if user.role == User.ROLE_ADMIN:
            return True

        # ✅ Owners can view/verify their own payments
        if view.action in ["retrieve", "verify", "verified", "list"]:
            return obj.user == user

        return False
