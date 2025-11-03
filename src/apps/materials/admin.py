from django.contrib import admin

from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "purity", "unit", "mixes_with_gold", "karat"]
    list_filter = ["mixes_with_gold", "unit"]
    search_fields = ["name"]
    list_editable = ["purity", "unit", "mixes_with_gold"]
