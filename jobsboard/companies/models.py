from django.db import models
from django.conf import settings
from django.core.validators import URLValidator, MinLengthValidator
from django.core.exceptions import ValidationError


def validate_https(url):
    """Ensure that a given URL starts with HTTPS."""
    validator = URLValidator(schemes=['https'])
    try:
        validator(url)
    except ValidationError:
        raise ValidationError("Website URL must use HTTPS.")


# ---------------------------------------------------------
# Industry Model
# ---------------------------------------------------------
# Represents an industry category for companies (e.g., IT, Healthcare).
# - Used to group companies under a specific industry.
# - Provides ordering by ID for consistent listing.
class Industry(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'companies'
        verbose_name_plural = "Industries"
        ordering = ["id"]

    def __str__(self):
        return self.name
    

# ---------------------------------------------------------
# Company Model
# ---------------------------------------------------------
# Represents a company registered in the jobs board system.
# - Contains details like name, description, logo, website, industry, and location.
# - Website must use HTTPS (validated by custom validator).
# - Associated with an owner (User) who manages the company profile.
# - Enforces uniqueness: a single user cannot register the same company name twice.
# - Includes indexes for faster lookups on name, industry, and owner.
class Company(models.Model):
    name = models.CharField(
        max_length=255,
        validators=[
            MinLengthValidator(2, message="Company name must be at least 2 characters long.")
        ]
    )
    description = models.TextField(
        validators=[
            MinLengthValidator(10, message="Description must be at least 10 characters.")
        ]
    )
    logo = models.ImageField(upload_to='company_logos/', blank=False)
    website = models.URLField(
        blank=True,
        null=True,
        validators=[validate_https],
    )

    industry = models.ForeignKey(
        Industry, 
        on_delete=models.CASCADE, 
        related_name='companies'
    )
    location = models.CharField(
        max_length=255,
        validators=[
            MinLengthValidator(2, message="Location must be at least 8 characters.")
        ]
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='companies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'companies'
        verbose_name_plural = 'Companies'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'], name='idx_company_name'),
            models.Index(fields=['industry'], name='idx_company_industry'),
            models.Index(fields=['owner'], name='idx_company_owner'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['name', 'owner'], name='unique_company_per_owner')
        ]

    def __str__(self):
        return self.name
