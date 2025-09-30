#jobsboard/users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from PIL import Image

from companies.models import Company

# ---------------------------------------------------------
# CustomUserManager
# ---------------------------------------------------------
# Custom manager for the User model.
# - Handles user creation with proper role assignments.
# - Automatically sets is_staff and is_superuser flags for admins.
# - Ensures password hashing when creating users.
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if extra_fields.get('role') == User.ROLE_ADMIN:
            extra_fields['is_staff'] = True
        if username == 'admin':  # only admin gets full superuser
            extra_fields['is_superuser'] = True
        

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password) # password hashed
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


# ---------------------------------------------------------
# User Model
# ---------------------------------------------------------
# Custom user model extending AbstractUser.
# - Supports three roles: Job Seeker, Employer, Admin.
# - Associates employees with a company.
# - Provides helper properties: is_seeker, is_recruiter, is_admin.
# - Integrates with Django permissions and groups.
# - Overrides __str__ to include username and role.
class User(AbstractUser):
    ROLE_SEEKER = 'SEEKER'
    ROLE_EMPLOYER = 'EMPLOYER'
    ROLE_ADMIN = 'ADMIN'

    ROLE_CHOICES = [
        (ROLE_SEEKER, 'Job Seeker'),
        (ROLE_EMPLOYER, 'Employer'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    ROLE_PERMISSIONS = {
        ROLE_SEEKER: ['view_user'],
        ROLE_EMPLOYER: ['change_user_role'],
        ROLE_ADMIN: ['change_user_role', 'deactivate_user'],
    }

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default=ROLE_SEEKER)
        # seekers/employees can belong to one company
    company = models.ForeignKey(
        Company,
        related_name="employees",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        app_label = 'users'
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
        return self.role == self.ROLE_EMPLOYER

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN


# ----------------------------
# Signals to assign groups and permissions
# ----------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_group_and_permissions(sender, instance, created, **kwargs):
    """Assign user to the proper group and add permissions."""
    if created:
        group_name = {
            User.ROLE_SEEKER: 'Job Seekers',
            User.ROLE_EMPLOYER: 'Employers',
            User.ROLE_ADMIN: 'Administrators'
        }.get(instance.role)

        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            perms = Permission.objects.filter(codename__in=User.ROLE_PERMISSIONS.get(instance.role, []))
            group.permissions.set(perms)
            instance.groups.add(group)



# ---------------------------------------------------------
# UserFile Model
# ---------------------------------------------------------
# Represents user-uploaded files (profile image, resume, CV).
# - Enforces file type restrictions and size validation.
# - Ensures unique file type per user.
# - Automatically validates and saves files with proper validators.
def validate_file_size(value):
    max_size_mb = 5
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Max file size is {max_size_mb}MB")


class UserFile(models.Model):
    FILE_TYPES = [
        ('profile_image', 'Profile Image'),
        ('resume', 'Resume'),
        ('cv', 'CV'),
    ]

    FILE_VALIDATORS = {
        'resume': [FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx']), validate_file_size],
        'cv': [FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx']), validate_file_size],
        'profile_image': [FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='files')
    file_type = models.CharField(max_length=50, choices=FILE_TYPES)
    file = models.FileField(upload_to='user_files/', validators=[])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'users'
        unique_together = ('user', 'file_type')

    def save(self, *args, **kwargs):
        validators = self.FILE_VALIDATORS.get(self.file_type)
        if validators:
            self.file.field.validators = validators
            self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.file_type}"

# ---------------------------------------------------------
# Profile Model
# ---------------------------------------------------------
# Stores additional user information such as bio, location, birth_date, and profile_image.
# - Profile is automatically created upon user creation.
# - Profile images are cropped/resized to 320x320 pixels.
# - Linked one-to-one with the User model.
# - Overrides __str__ to show the username's profile.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Only .jpg, .jpeg, .png allowed. Will be cropped to 320x320."
    )

    class Meta:
        app_label = 'users'

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_image:
            img_path = self.profile_image.path
            img = Image.open(img_path)
            img = img.convert('RGB')
            img = img.resize((320, 320), Image.Resampling.LANCZOS)
            img.save(img_path)



# ---------------------------------------------------------
# Signals
# ---------------------------------------------------------
# Assign user to the proper group and permissions on creation.
# Automatically create or update Profile when User is created or updated.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        profile = getattr(instance, 'profile', None)
        if profile:
            profile.save()

