from rest_framework.permissions import BasePermission


class IsCompanyOwner(BasePermission):
    """
    Only allow users who own a company to create or delete jobs.
    """

    def has_permission(self, request, view):
        # You can refine by action if needed
        if view.action in ["create_job", "delete_job"]:
            return hasattr(request.user, "company")
        return True


class IsJobOwner(BasePermission):
    """
    Only allow the user who created the job to delete it.
    """

    def has_object_permission(self, request, view, obj):
        if view.action == "delete_job":
            return obj.created_by == request.user
        return True
