# jobsboard/jobs/permissions.py
from rest_framework import permissions
from users.models import User 

class JobPermission(permissions.BasePermission):
    """
    - Public: can list/retrieve jobs
    - Job Seeker: can list/retrieve jobs + apply
    - Recruiter/Admin: full access (create, update, delete)
    """

    def has_permission(self, request, view):
        # Everyone can list/retrieve
        if view.action in ["list", "retrieve"]:
            return True

        # Must be authenticated beyond this point
        if not (request.user and request.user.is_authenticated):
            return False

        # Job Seekers: only allowed to 'apply' action
        if request.user.role == User.ROLE_SEEKER:
            return view.action == "apply"

        # Recruiters & Admins: full access
        return request.user.role in [User.ROLE_EMPLOYER, User.ROLE_ADMIN]
