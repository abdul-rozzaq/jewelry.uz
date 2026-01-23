import json
import logging

from django.utils import timezone
from typing import Optional

from django.conf import settings
from pywebpush import webpush, WebPushException

from apps.transactions.models import Transaction
from .models import PushSubscription, NotificationType, Notification

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending web push notifications"""

    @staticmethod
    def send_push_notification(user_id: int, title: str, message: str, notification_type: str, object_id: Optional[int] = None, organization_id: Optional[int] = None) -> bool:
        """
        Send push notification to user's active subscriptions
        """
        try:
            # Get user's active subscriptions
            subscriptions = PushSubscription.objects.filter(user_id=user_id, is_active=True)

            if not subscriptions.exists():
                logger.info(f"No active subscriptions found for user {user_id}")
                return False

            notification = Notification.objects.create(recipient_id=user_id, organization_id=organization_id, title=title, message=message, notification_type=notification_type, object_id=object_id)

            # Prepare payload
            payload = {"title": title, "body": message, "icon": "/static/icons/icon-192x192.png", "badge": "/static/icons/badge-72x72.png", "data": {"notification_id": notification.id, "type": notification_type, "object_id": object_id, "timestamp": timezone.now().isoformat()}, "actions": [{"action": "view", "title": "View"}, {"action": "dismiss", "title": "Dismiss"}], "requireInteraction": True, "timestamp": timezone.now().timestamp() * 1000}  # Customize as needed  # Customize as needed

            # Send to all subscriptions
            success_count = 0
            errors = []

            # Get VAPID configuration
            vapid_config = PushNotificationService.get_vapid_claims()

            if not vapid_config:
                logger.error("VAPID keys not configured properly")
                return False

            for subscription in subscriptions:
                try:
                    webpush(subscription_info={"endpoint": subscription.endpoint, "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth}}, data=json.dumps(payload), vapid_private_key=vapid_config["vapid_private_key"], vapid_claims=vapid_config["vapid_claims"])
                    success_count += 1

                except WebPushException as e:
                    error_msg = f"WebPush error for subscription {subscription.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

                    # If subscription is invalid, mark as inactive
                    if e.response and e.response.status_code in [400, 410]:
                        subscription.is_active = False
                        subscription.save()

                except Exception as e:
                    error_msg = f"Unexpected error for subscription {subscription.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            # Update notification record
            if success_count > 0:
                notification.is_pushed = True
                notification.push_sent_at = timezone.now()

            if errors:
                notification.push_error = "; ".join(errors)

            notification.save()

            logger.info(f"Push notification sent to {success_count}/{subscriptions.count()} subscriptions for user {user_id}")
            return success_count > 0

        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False

    @staticmethod
    def send_transaction_notification(transaction_id: int, notification_type: str, recipient_user_id: int) -> bool:
        """
        Send transaction-related push notification
        """
        try:

            transaction = Transaction.objects.select_related("sender", "receiver").get(id=transaction_id)

            # Prepare message based on type
            if notification_type == NotificationType.TRANSACTION_CREATED:
                title = "New Transaction"
                message = f"You have received a new transaction from {transaction.sender.name}"
            elif notification_type == NotificationType.TRANSACTION_ACCEPTED:
                title = "Transaction Accepted"
                message = f"Your transaction to {transaction.receiver.name} has been accepted"
            else:
                title = "Transaction Update"
                message = f"Transaction #{transaction.id} has been updated"

            return PushNotificationService.send_push_notification(user_id=recipient_user_id, title=title, message=message, notification_type=notification_type, object_id=transaction_id, organization_id=transaction.receiver.id if notification_type == NotificationType.TRANSACTION_CREATED else transaction.sender.id)

        except Exception as e:
            logger.error(f"Error sending transaction notification: {str(e)}")
            return False

    @staticmethod
    def get_vapid_claims():
        """Get VAPID claims for push notifications"""
        try:
            vapid_private_key = getattr(settings, "VAPID_PRIVATE_KEY", None)
            vapid_public_key = getattr(settings, "VAPID_PUBLIC_KEY", None)

            if vapid_private_key and vapid_public_key:
                return {"vapid_private_key": vapid_private_key, "vapid_claims": {"sub": getattr(settings, "VAPID_SUBJECT", "mailto:admin@jewelry.uz")}}

            return None

        except Exception as e:
            logger.error(f"Error loading VAPID keys: {str(e)}")
            return None
