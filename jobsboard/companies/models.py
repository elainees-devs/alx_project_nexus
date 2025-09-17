from django.db import models
from django.conf import settings


class Industry(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Industries"

    def __str__(self):
        return self.name
    

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to='company_logos/', blank=False)
    website = models.URLField(blank=True, null=True)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE,related_name='companies')
    location = models.CharField(max_length=255, blank=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
