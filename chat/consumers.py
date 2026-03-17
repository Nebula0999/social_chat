"""
WebSocket consumers for chat app.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message, MessageRead, TypingIndicator

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for chat functionality.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Clear typing indicator
        await self.clear_typing_indicator()

    async def receive(self, text_data):
        """Receive message from WebSocket."""
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'typing_start':
            await self.handle_typing_start()
        elif message_type == 'typing_stop':
            await self.handle_typing_stop()
        elif message_type == 'message_read':
            await self.handle_message_read(data)

    async def handle_chat_message(self, data):
        """Handle incoming chat message."""
        content = data['content']

        # Save message to database
        message = await self.save_message(content)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': {
                        'id': message.sender.id,
                        'username': message.sender.username,
                    },
                    'created_at': message.created_at.isoformat(),
                }
            }
        )

    async def handle_typing_start(self):
        """Handle typing start event."""
        await self.set_typing_indicator(True)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_event',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': True,
            }
        )

    async def handle_typing_stop(self):
        """Handle typing stop event."""
        await self.set_typing_indicator(False)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_event',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': False,
            }
        )

    async def handle_message_read(self, data):
        """Handle message read receipt."""
        message_id = data.get('message_id')
        await self.mark_message_read(message_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_read',
                'message_id': message_id,
                'user_id': self.user.id,
            }
        )

    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def typing_event(self, event):
        """Send typing event to WebSocket."""
        # Don't send typing events back to the sender
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_event',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))

    async def message_read(self, event):
        """Send message read receipt to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
        }))

    @database_sync_to_async
    def save_message(self, content):
        """Save message to database."""
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content
        )
        return message

    @database_sync_to_async
    def set_typing_indicator(self, is_typing):
        """Set or clear typing indicator."""
        conversation = Conversation.objects.get(id=self.conversation_id)
        if is_typing:
            TypingIndicator.objects.update_or_create(
                conversation=conversation,
                user=self.user
            )
        else:
            TypingIndicator.objects.filter(
                conversation=conversation,
                user=self.user
            ).delete()

    @database_sync_to_async
    def clear_typing_indicator(self):
        """Clear typing indicator on disconnect."""
        TypingIndicator.objects.filter(
            conversation_id=self.conversation_id,
            user=self.user
        ).delete()

    @database_sync_to_async
    def mark_message_read(self, message_id):
        """Mark message as read."""
        try:
            message = Message.objects.get(id=message_id)
            MessageRead.objects.get_or_create(
                message=message,
                user=self.user
            )
        except Message.DoesNotExist:
            pass
