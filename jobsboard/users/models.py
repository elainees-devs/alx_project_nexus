#jobsboard/users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from PIL import Image

# ----------------------------
# Custom User Manager
# ----------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if extra_fields.get('role') == User.ROLE_ADMIN:
            extra_fields['is_staff'] = True
        if username == 'admin':  # only developer gets full superuser
            extra_fields['is_superuser'] = True
        

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


# ----------------------------
# Custom User Model
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
        ROLE_SEEKER: ['view_user'],
        ROLE_RECRUITER: ['change_user_role'],
        ROLE_ADMIN: ['change_user_role', 'deactivate_user'],
    }

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default=ROLE_SEEKER)
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
        return self.role == self.ROLE_RECRUITER

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
            User.ROLE_RECRUITER: 'Recruiters',
            User.ROLE_ADMIN: 'Administrators'
        }.get(instance.role)

        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            perms = Permission.objects.filter(codename__in=User.ROLE_PERMISSIONS.get(instance.role, []))
            group.permissions.set(perms)
            instance.groups.add(group)


# ----------------------------
# UserFile Model
# ----------------------------
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


# ----------------------------
# Profile Model
# ----------------------------
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


# ----------------------------
# Signal to create Profile on User creation
# ----------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
