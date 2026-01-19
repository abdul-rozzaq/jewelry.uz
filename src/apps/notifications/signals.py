from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

from apps.transactions.models import Transaction, TransactionStatuses
from .models import NotificationType
from .services import PushNotificationService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Transaction)
def handle_transaction_created(sender, instance, created, **kwargs):
    """
    Handle Transaction creation and status changes
    """
    print("Signal triggered for Transaction:", instance.id, "Created:", created)
    
    if created:
        # Transaction yaratilganda receiver organizatsiyaning userlariga notification yuborish
        try:
            # Receiver organization userlarini olish
            receiver_users = instance.receiver.users.filter(is_active=True)

            print(receiver_users)

            for user in receiver_users:
                PushNotificationService.send_transaction_notification(transaction_id=instance.id, notification_type=NotificationType.TRANSACTION_CREATED, recipient_user_id=user.id)

            logger.info(f"Transaction created notifications sent for transaction {instance.id}")

        except Exception as e:
            logger.error(f"Error sending transaction created notifications: {str(e)}")

    else:
        # Status o'zgarish bo'yicha notification
        if hasattr(instance, "_original_status"):
            old_status = instance._original_status
            new_status = instance.status

            if old_status != new_status and new_status == TransactionStatuses.ACCEPTED:
                # Transaction qabul qilinganida sender organizatsiyaga notification
                try:
                    sender_users = instance.sender.users.filter(is_active=True)

                    for user in sender_users:
                        PushNotificationService.send_transaction_notification(transaction_id=instance.id, notification_type=NotificationType.TRANSACTION_ACCEPTED, recipient_user_id=user.id)

                    logger.info(f"Transaction accepted notifications sent for transaction {instance.id}")

                except Exception as e:
                    logger.error(f"Error sending transaction accepted notifications: {str(e)}")


@receiver(post_save, sender=Transaction)
def track_transaction_status_changes(sender, instance, **kwargs):
    """
    Track original status for comparison in post_save
    """
    if instance.pk:  # Only for existing instances
        try:
            original = Transaction.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except Transaction.DoesNotExist:
            instance._original_status = None
