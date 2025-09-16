from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# ----------------------------
# Custom user manager
# ----------------------------
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
        return self.create_user(username, email, password, **extra_fields)


# ----------------------------
# Custom User model
# ----------------------------
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
        'Recruiter': ['change_user_role'],
        'Administrator': ['change_user_role', 'deactivate_user'],
    }

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default=ROLE_SEEKER)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        app_label = 'users'  # critical for Django to recognize app
        permissions = [
            ('change_user_role', 'Can Change User Role'),
            ('deactivate_user', 'Can Deactivate User'),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_seeker(self):
        return self.role == self.ROLE_SEEKER

    @property
    def is_recruiter(self):
        return self.role == self.ROLE_RECRUITER

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN


# ----------------------------
# Signals to assign groups and permissions
# ----------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_group_and_permissions(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.role == instance.ROLE_SEEKER:
        group_name = 'Job Seekers'
    elif instance.role == instance.ROLE_RECRUITER:
        group_name = 'Recruiters'
    elif instance.role == instance.ROLE_ADMIN:
        group_name = 'Administrators'
    else:
        return

    group, _ = Group.objects.get_or_create(name=group_name)
    role_name = dict(instance.ROLE_CHOICES).get(instance.role)
    if role_name:
        perm_codenames = instance.ROLE_PERMISSIONS.get(role_name, [])
        perms = Permission.objects.filter(codename__in=perm_codenames)
        group.permissions.add(*perms)

    instance.groups.add(group)


# ----------------------------
# UserFile model
# ----------------------------
class UserFile(models.Model):
    FILE_TYPES = [
        ('profile_image', 'Profile Image'),
        ('resume', 'Resume'),
        ('cv', 'CV'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file_type = models.CharField(max_length=50, choices=FILE_TYPES)
    file = models.FileField(upload_to='user_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'users'

    def __str__(self):
        return f"{self.user.username} - {self.file_type}"


# ----------------------------
# Profile model
# ----------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(
        upload_to='profile_images/', null=True, blank=True,
        help_text="Requires Pillow library: pip install Pillow"
    )

    class Meta:
        app_label = 'users'

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
