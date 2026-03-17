"""
Tests for chat app.
"""
import pytest
from django.contrib.auth import get_user_model
from chat.models import Conversation, Message

User = get_user_model()


@pytest.mark.django_db
class TestConversationModel:
    def test_create_direct_conversation(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass')
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass')

        conversation = Conversation.objects.create(conversation_type='direct')
        conversation.participants.add(user1, user2)

        assert conversation.conversation_type == 'direct'
        assert conversation.participants.count() == 2

    def test_create_group_conversation(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass')
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass')

        conversation = Conversation.objects.create(
            name='Test Group',
            conversation_type='group'
        )
        conversation.participants.add(user1, user2)

        assert conversation.conversation_type == 'group'
        assert conversation.name == 'Test Group'
        assert conversation.participants.count() == 2


@pytest.mark.django_db
class TestMessageModel:
    def test_create_message(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass')
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass')

        conversation = Conversation.objects.create(conversation_type='direct')
        conversation.participants.add(user1, user2)

        message = Message.objects.create(
            conversation=conversation,
            sender=user1,
            content='Hello, World!'
        )

        assert message.conversation == conversation
        assert message.sender == user1
        assert message.content == 'Hello, World!'
