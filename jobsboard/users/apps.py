# users/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db import connection


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        post_migrate.connect(reset_profile_sequence, sender=self)


def reset_profile_sequence(sender, **kwargs):
    """
    Reset sequence for users_profile so new rows get the correct ID.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT setval(
              pg_get_serial_sequence('"users_profile"', 'id'),
              COALESCE((SELECT MAX(id) FROM "users_profile"), 1),
              TRUE
            );
        """)
