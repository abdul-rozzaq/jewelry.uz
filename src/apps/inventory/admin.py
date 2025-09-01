from django.contrib import admin
from .models import OrganizationInventory


@admin.register(OrganizationInventory)
class OrganizationInventoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrganizationInventory._meta.fields]
    search_fields = [field.name for field in OrganizationInventory._meta.fields if field.get_internal_type() in ["CharField", "TextField"]]
    list_filter = [field.name for field in OrganizationInventory._meta.fields if field.get_internal_type() in ["BooleanField", "DateField", "DateTimeField", "ForeignKey"]]
