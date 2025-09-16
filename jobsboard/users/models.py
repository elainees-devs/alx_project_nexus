from django.contrib.auth.models import Group, AbstractUser, BaseUserManager, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

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

    ROLE_PERMISSIONS = {
        'Job Seeker': ['view_user'],
        'Recruiter': ['add_user', 'view_user', 'change_user_role'],
        'Administrator': ['add_user', 'view_user', 'change_user_role', 'deactivate_user'],
    }

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default=ROLE_SEEKER)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        permissions = [
            ('add_user', 'Can Add User'),
            ('view_user', 'Can View User'),
            ('change_user_role', 'Can Change User Role'),
            ('deactivate_user', 'Can Deactivate User'),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # Role check properties
    @property
    def is_seeker(self):
        return self.role == self.ROLE_SEEKER

    @property
    def is_recruiter(self):
        return self.role == self.ROLE_RECRUITER

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN


# Signal to assign group and permissions
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_group_and_permissions(sender, instance, created, **kwargs):
    if not created:
        return

    # Determine group name based on role
    if instance.role == instance.ROLE_SEEKER:
        group_name = 'Job Seekers'
    elif instance.role == instance.ROLE_RECRUITER:
        group_name = 'Recruiters'
    elif instance.role == instance.ROLE_ADMIN:
        group_name = 'Administrators'
    else:
        return

    # Get or create the group
    group, _ = Group.objects.get_or_create(name=group_name)

    # Assign permissions to the group (only if missing)
    role_name = dict(instance.ROLE_CHOICES).get(instance.role)
    if role_name:
        perm_codenames = instance.ROLE_PERMISSIONS.get(role_name, [])
        perms = Permission.objects.filter(codename__in=perm_codenames)
        group.permissions.add(*perms)

    # Add user to the group
    instance.groups.add(group)

# Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Signal to automatically create/update Profile when User is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()