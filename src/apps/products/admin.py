from django.contrib import admin
from .models import Product, ProductGenealogy


class GenealogyInline(admin.TabularInline):
    model = ProductGenealogy
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "material", "organization", "quantity", "created_at"]
    search_fields = ["material__name", "organization__name"]
    list_filter = ["created_at", "material", "organization"]

    inlines = [GenealogyInline]


@admin.register(ProductGenealogy)
class ProductGenealogyAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "material", "percent"]
    search_fields = ["product__material__name", "material__name"]
    list_filter = ["percent"]
