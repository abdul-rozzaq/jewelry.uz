from django.contrib import admin
from .models import (
    CoatProcess,
    GoldDowngradeProcess,
)

@admin.register(CoatProcess)
class CoatProcessAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "status", "gold_input", "iron_input", "created_at")
    list_filter = ("status", "organization")
    search_fields = ("id",)
    readonly_fields = ("total_in", "total_out", "pure_gold")

@admin.register(GoldDowngradeProcess)
class GoldDowngradeProcessAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "status", "gold_999_input", "gold_585_output", "created_at")
    list_filter = ("status", "organization")
    search_fields = ("id",)
    readonly_fields = ("total_in", "total_out", "pure_gold")
