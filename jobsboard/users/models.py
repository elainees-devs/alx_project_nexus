from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model extending AbstractUser to include roles
class User(AbstractUser):
    ROLE_SEEKER = 'SEEKER'
    ROLE_RECRUITER = 'RECRUITER'
    ROLE_ADMIN = 'ADMIN'

    ROLE_CHOICES = [
        (ROLE_SEEKER, 'Job Seeker'),
        (ROLE_RECRUITER, 'Recruiter'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default=ROLE_SEEKER,
    )

    # Role check methods
    def is_seeker(self): 
        return self.role == self.ROLE_SEEKER

    def is_recruiter(self):
        return self.role == self.ROLE_RECRUITER

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

   