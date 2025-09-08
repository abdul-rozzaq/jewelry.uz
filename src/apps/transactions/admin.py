from django.contrib import admin

from .models import Transaction, TransactionItem


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    fields = ["inventory", "quantity"]
    readonly_fields = ["inventory"]

    extra = 1


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "sender",
        "receiver",
        "status",
        "created_at",
    ]
    list_editable = ["sender", "receiver", "status"]
    inlines = [TransactionItemInline]
