from django.contrib import admin

from .models import Transaction, TransactionItem


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 1


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "sender",
        "receiver",
        "status",
        "created_at",
        "confirmed_by_sender",
        "confirmed_by_receiver",
    ]


    inlines = [TransactionItemInline]
