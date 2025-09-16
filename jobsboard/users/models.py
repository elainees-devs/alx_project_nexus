from django.contrib.auth.models import Group, AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Signal to assign user to a group based on their role
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_group_based_on_role(sender, instance, created, **kwargs):
    if created:
        if instance.role == instance.ROLE_SEEKER:
            group, _ = Group.objects.get_or_create(name='Job Seekers')
            instance.groups.add(group)
        elif instance.role == instance.ROLE_RECRUITER:
            group, _ = Group.objects.get_or_create(name='Recruiters')
            instance.groups.add(group)
        elif instance.role == instance.ROLE_ADMIN:
            group, _ = Group.objects.get_or_create(name='Administrators')
            instance.groups.add(group)

# Custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

# Custom user model
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

    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # Role check methods
    @property
    def is_seeker(self): 
        return self.role == self.ROLE_SEEKER

    @property
    def is_recruiter(self):
        return self.role == self.ROLE_RECRUITER

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN
