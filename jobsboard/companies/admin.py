from django.contrib import admin
from .models import Industry, Company

# Customize how the Industry model appears in admin  interface
class IndustryAdmin(admin.ModelAdmin):
    list_display=("id", "name") # columns to display
    search_fields=["name"]


class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description","website", "location", "industry")
    search_fields=["name", "location", "industry__name"]
    list_filter = ("industry",)
   

# Register the model with its custom admin configuration
admin.site.register(Industry,IndustryAdmin)
admin.site.register(Company, CompanyAdmin)

