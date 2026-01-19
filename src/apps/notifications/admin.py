from django.contrib import admin
from .models import Notification, PushSubscription


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "endpoint", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["user__username", "user__email", "endpoint"]
    readonly_fields = ["created_at"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "recipient", "notification_type", "status", "is_pushed", "created_at"]
    list_filter = ["notification_type", "status", "is_pushed", "created_at"]
    search_fields = ["title", "message", "recipient__username"]
    readonly_fields = ["created_at", "updated_at", "push_sent_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("recipient", "organization")
