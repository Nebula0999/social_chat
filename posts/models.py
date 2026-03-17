"""
Models for posts app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from common.models import TimeStampedModel
from common.utils import get_upload_path

User = get_user_model()


class Post(TimeStampedModel):
    """
    Post model for user posts.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=5000)
    image = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    likes = models.ManyToManyField(User, through='Like', related_name='liked_posts')
    repost_of = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reposts'
    )

    class Meta:
        db_table = 'posts'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return f'{self.author.username}: {self.content[:50]}'

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def repost_count(self):
        return self.reposts.count()


class Like(TimeStampedModel):
    """
    Like relationship between users and posts.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')

    class Meta:
        db_table = 'likes'
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user.username} likes {self.post.id}'


class Comment(TimeStampedModel):
    """
    Comment model for post comments.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    class Meta:
        db_table = 'comments'
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]

    def __str__(self):
        return f'{self.author.username} on {self.post.id}: {self.content[:30]}'
