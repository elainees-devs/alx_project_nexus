# jobsboard/applications/admin.py
from django.contrib import admin
from .models import Application, ApplicationFile


# ----------------------------
# ApplicationFile Inline
# ----------------------------
class ApplicationFileInline(admin.TabularInline):
    """Inline form for ApplicationFile inside Application admin."""
    model = ApplicationFile
    extra = 1  # Number of empty forms to display


# ----------------------------
# Application Admin
# ----------------------------
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin configuration for Application model."""
    list_display = ("id", "job", "applicant", "status", "applied_at", "ip_address")
    list_filter = ("status", "applied_at")
    search_fields = ("job__title", "applicant__username", "applicant__email")
    inlines = [ApplicationFileInline]
    ordering = ("-applied_at",)


# ----------------------------
# ApplicationFile Admin
# ----------------------------
@admin.register(ApplicationFile)
class ApplicationFileAdmin(admin.ModelAdmin):
    """Admin configuration for ApplicationFile model."""
    list_display = ("id", "application", "file_type", "file_path", "uploaded_at")
    list_filter = ("file_type", "uploaded_at")
    search_fields = ("application__job__title", "application__applicant__username")
    ordering = ("-uploaded_at",)
