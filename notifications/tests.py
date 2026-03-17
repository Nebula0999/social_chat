"""
Tests for notifications app.
"""
import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()


@pytest.mark.django_db
class TestNotificationModel:
    def test_create_notification(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass')
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass')

        notification = Notification.objects.create(
            recipient=user1,
            sender=user2,
            notification_type='like',
            message='user2 liked your post'
        )

        assert notification.recipient == user1
        assert notification.sender == user2
        assert notification.notification_type == 'like'
        assert notification.is_read == False

    def test_mark_notification_read(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass')

        notification = Notification.objects.create(
            recipient=user1,
            notification_type='follow',
            message='Someone followed you'
        )

        assert notification.is_read == False

        notification.is_read = True
        notification.save()

        assert notification.is_read == True
