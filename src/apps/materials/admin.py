from django.contrib import admin

from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "purity", "unit", "karat"]
    list_filter = []
    search_fields = ["name"]
    list_editable = ["purity", "unit"]
