from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]
    search_fields = [field.name for field in Product._meta.fields if field.get_internal_type() in ["CharField", "TextField"]]
    list_filter = [field.name for field in Product._meta.fields if field.get_internal_type() in ["BooleanField", "DateField", "DateTimeField", "ForeignKey"]]
