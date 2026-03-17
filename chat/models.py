"""
Models for chat app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from common.models import TimeStampedModel
from common.utils import get_upload_path

User = get_user_model()


class Conversation(TimeStampedModel):
    """
    Conversation model for chat.
    """
    CONVERSATION_TYPES = [
        ('direct', 'Direct Message'),
        ('group', 'Group Chat'),
    ]

    name = models.CharField(max_length=255, blank=True)
    conversation_type = models.CharField(
        max_length=10,
        choices=CONVERSATION_TYPES,
        default='direct'
    )
    participants = models.ManyToManyField(User, related_name='conversations')

    class Meta:
        db_table = 'conversations'
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        if self.name:
            return self.name
        return f'Conversation {self.id}'

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class Message(TimeStampedModel):
    """
    Message model for chat messages.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(max_length=5000)
    file = models.FileField(upload_to=get_upload_path, null=True, blank=True)
    read_by = models.ManyToManyField(User, through='MessageRead', related_name='read_messages')

    class Meta:
        db_table = 'messages'
        indexes = [
            models.Index(fields=['conversation', '-created_at']),
        ]

    def __str__(self):
        return f'{self.sender.username}: {self.content[:30]}'


class MessageRead(TimeStampedModel):
    """
    Track message read receipts.
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reads')

    class Meta:
        db_table = 'message_reads'
        unique_together = ('message', 'user')
        indexes = [
            models.Index(fields=['message', 'user']),
        ]

    def __str__(self):
        return f'{self.user.username} read {self.message.id}'


class TypingIndicator(models.Model):
    """
    Track typing indicators in conversations.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'typing_indicators'
        unique_together = ('conversation', 'user')

    def __str__(self):
        return f'{self.user.username} typing in {self.conversation.id}'
