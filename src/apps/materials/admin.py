from django.contrib import admin

from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "purity", "unit", "mixes_with_gold", "karat", "is_scrap"]
    list_filter = ["mixes_with_gold", "unit", "is_scrap"]
    search_fields = ["name"]
    list_editable = ["purity", "unit", "mixes_with_gold", "is_scrap"]