"""
Utility functions for creating notifications.
"""
from .models import Notification


def create_notification(recipient, sender, notification_type, message, content_object=None):
    """
    Create a notification.
    """
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        message=message,
        content_object=content_object
    )
    return notification
