"""
Admin configuration for chat app.
"""
from django.contrib import admin
from .models import Conversation, Message, MessageRead, TypingIndicator


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'conversation_type', 'created_at']
    list_filter = ['conversation_type', 'created_at']
    search_fields = ['name']
    filter_horizontal = ['participants']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['sender__username', 'content']
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        return obj.content[:50]


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']


@admin.register(TypingIndicator)
class TypingIndicatorAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'user', 'timestamp']
    list_filter = ['timestamp']
