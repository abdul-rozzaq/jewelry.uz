from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets     = BaseUserAdmin.fieldsets     + (("Extra Info", {"fields": ("role", "organization")}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (("Extra Info", {"fields": ("role", "organization")}),)
    list_display  = ("username", "role", "organization", "is_staff", "is_active")
    list_filter   = ("role", "organization", "is_staff", "is_active")
    search_fields = ("username", "organization__name")
