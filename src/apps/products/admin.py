from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import Product


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        is_composite = cleaned.get("is_composite")
        pure_gold = cleaned.get("pure_gold")
        quantity = cleaned.get("quantity")

        # pure_gold must not exceed total quantity
        if pure_gold is not None and quantity is not None and pure_gold > quantity:
            raise ValidationError({"pure_gold": "pure_gold cannot be greater than quantity."})

        if is_composite:
            if pure_gold is None or pure_gold <= 0:
                raise ValidationError({"pure_gold": "pure_gold is required and must be > 0 for composite products."})

        return cleaned


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = [
        "id",
        "material",
        "project",
        "organization",
        "quantity",
        "purity",
        "is_composite",
        "pure_gold",
        "karat",
        "created_at",
    ]
    search_fields = ["material__name", "organization__name"]
    list_filter = ["created_at", "material", "organization", "is_composite"]
    list_editable = ["quantity", "project", "purity", "is_composite", "pure_gold"]

    def karat(self, obj):
        return obj.karat

    karat.short_description = "Karat"
