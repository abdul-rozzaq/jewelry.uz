from django.db import models
from apps.common.models import BaseModel
from apps.organizations.models import Organization
from apps.users.models import User


class NotificationType(models.TextChoices):
    TRANSACTION_CREATED = "transaction_created", "Transaction Created"
    TRANSACTION_ACCEPTED = "transaction_accepted", "Transaction Accepted"
    TRANSACTION_REJECTED = "transaction_rejected", "Transaction Rejected"


class NotificationStatus(models.TextChoices):
    UNREAD = "unread", "Unread"
    READ = "read", "Read"


class PushSubscription(models.Model):
    """Store user's push notification subscription data"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="push_subscriptions")
    endpoint = models.URLField(max_length=500)
    p256dh = models.CharField(max_length=255)  # Public key
    auth = models.CharField(max_length=255)  # Auth secret
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "endpoint")
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"Push subscription for {self.user.username}"


class Notification(BaseModel):
    """Store notification data"""

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)

    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)
    status = models.CharField(max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.UNREAD)

    # Reference to the related object (transaction, product, etc.)
    object_id = models.PositiveIntegerField(null=True, blank=True)

    # Push notification metadata
    is_pushed = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True, blank=True)
    push_error = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "status"]),
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["notification_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

    def mark_as_read(self):
        """Mark notification as read"""
        self.status = NotificationStatus.READ
        self.save(update_fields=["status", "updated_at"])
