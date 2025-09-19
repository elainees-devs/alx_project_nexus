# jobsboard/applications/models.py
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


def validate_file_size(file):
    """Validate that file size is not greater than 5MB."""
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError(f"File size must be under {max_size/1024/1024}MB.")


class Application(models.Model):
    # Enum choices
    APPLICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('interview', 'Interview'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    ]

    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE)
    applicant = models.ForeignKey('users.User', on_delete=models.CASCADE)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES)
    applied_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_applications"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['job', 'applicant']
        indexes = [
            models.Index(fields=['job'], name='idx_applications_job'),
            models.Index(fields=['applicant'], name='idx_applications_applicant'),
            models.Index(fields=['status'], name='idx_applications_status'),
            models.Index(fields=['reviewed_by'], name='idx_applications_reviewed_by'),  
            models.Index(fields=['applied_at'], name='idx_applications_applied_at'),
        ]

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"


class ApplicationFile(models.Model):
    FILE_TYPES = [
        ('resume', 'Resume'),
        ('cv', 'Curriculum Vitae'),
        ('cover_letter', 'Cover Letter'),
    ]

    FILE_VALIDATORS = {
        'resume': [FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx']), validate_file_size],
        'cv': [FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx']), validate_file_size],
        'cover_letter': [FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt']), validate_file_size],
    }

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='files')
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    file_path = models.CharField(max_length=255) 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.application}"
