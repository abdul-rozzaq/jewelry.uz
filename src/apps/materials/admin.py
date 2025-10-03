from django.contrib import admin

from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "parent", "purity", "unit"]
    list_filter = []
    search_fields = ["name"]
