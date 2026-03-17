"""
Admin configuration for posts app.
"""
from django.contrib import admin
from .models import Post, Like, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'content']
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        return obj.content[:50]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'content']

    def content_preview(self, obj):
        return obj.content[:50]
