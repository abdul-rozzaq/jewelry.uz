from django.contrib import admin

from apps.projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active", "created_at"]
    search_fields = ["name", "description"]
    list_filter = ["is_active", "created_at"]
