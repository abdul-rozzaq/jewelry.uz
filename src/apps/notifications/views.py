from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Notification, PushSubscription
from .serializers import PushSubscriptionSerializer, NotificationListSerializer

from apps.common.serializers import EmptySerializer


class SubscribePushView(generics.CreateAPIView):
    """Subscribe user to push notifications"""

    serializer_class = PushSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()

        return Response({"message": "Successfully subscribed to push notifications", "subscription_id": subscription.id}, status=status.HTTP_201_CREATED)


class UnsubscribePushView(generics.CreateAPIView):
    """Unsubscribe user from push notifications"""

    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        endpoint = request.data.get("endpoint")

        if not endpoint:
            return Response({"error": "Endpoint is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subscription = PushSubscription.objects.get(user=request.user, endpoint=endpoint)
            subscription.delete()
            # subscription.is_active = False
            # subscription.save()

            return Response({"message": "Successfully unsubscribed from push notifications"}, status=status.HTTP_200_OK)

        except PushSubscription.DoesNotExist:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)


class NotificationListView(generics.ListAPIView):
    """List user's notifications"""

    serializer_class = NotificationListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related("organization")


class MarkAsReadView(generics.UpdateAPIView):
    """Mark notification as read"""
    serializer_class = EmptySerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)

        notification.mark_as_read()

        return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
