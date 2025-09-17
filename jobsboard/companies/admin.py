from django.contrib import admin
from .models import Industry, Company

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")  # columns to display
    search_fields = ["name"]        # searchable fields

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "website", "location", "industry")
    search_fields = ["name", "location", "industry__name"]
    list_filter = ("industry",)
