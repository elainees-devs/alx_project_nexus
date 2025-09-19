#jobsboard/payments/permissions.py
from rest_framework import permissions

class PaymentPermission(permissions.BasePermission):
    """
    Custom rules for payments:
    - All authenticated users can create (initiate) and verify their own payments.
    - Users can list/retrieve only their own payments.
    - Updates and deletes are restricted to admins.
    """

    def has_permission(self, request, view):
        # Must be logged in
        if not request.user or not request.user.is_authenticated:
            return False

        # Everyone can use custom actions 'initiate' and 'verify'
        if view.action in ["initiate", "verify", "verified"]:
            return True

        # Only admins can update/destroy
        if view.action in ["update", "partial_update", "destroy"]:
            return request.user.is_staff or request.user.is_superuser

        # List/retrieve is allowed for all authenticated users
        if view.action in ["list", "retrieve", "create"]:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # Admins can always act
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Otherwise, user must own the payment
        return obj.user == request.user
