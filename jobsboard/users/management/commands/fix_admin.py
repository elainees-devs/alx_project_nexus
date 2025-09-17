from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Ensure admin user has proper role and permissions'

    def handle(self, *args, **kwargs):
        username = 'admin'  # admin username
        try:
            admin_user = User.objects.get(username=username)
            admin_user.role = User.ROLE_ADMIN
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(
                f"Admin {username} updated: role={admin_user.role}, is_staff={admin_user.is_staff}, is_superuser={admin_user.is_superuser}"
            ))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User {username} does not exist."))
