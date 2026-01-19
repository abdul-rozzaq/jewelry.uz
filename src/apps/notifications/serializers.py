from rest_framework import serializers
from .models import Notification, PushSubscription


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ["endpoint", "p256dh", "auth"]

    def create(self, validated_data):
        # Get user from context
        user = self.context["request"].user

        # Check if subscription already exists
        subscription, created = PushSubscription.objects.get_or_create(user=user, endpoint=validated_data["endpoint"], defaults={"p256dh": validated_data["p256dh"], "auth": validated_data["auth"], "is_active": True})

        if not created:
            # Update existing subscription
            subscription.p256dh = validated_data["p256dh"]
            subscription.auth = validated_data["auth"]
            subscription.is_active = True
            subscription.save()

        return subscription


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "message", "notification_type", "status", "object_id", "created_at"]
        read_only_fields = ["id", "created_at"]


class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "message", "notification_type", "status", "created_at"]
