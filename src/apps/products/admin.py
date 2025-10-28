from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "material", "project", "organization", "quantity", "purity", "karat", "created_at"]
    search_fields = ["material__name", "organization__name"]
    list_filter = ["created_at", "material", "organization"]
    list_editable = ["quantity", "project", "purity"]

    def karat(self, obj):
        return obj.karat

    karat.short_description = "Karat"
