"""
User models for authentication and profiles.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from common.models import TimeStampedModel
from common.utils import get_upload_path


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    followers = models.ManyToManyField(
        'self',
        through='Follow',
        symmetrical=False,
        related_name='following_users'
    )

    def __str__(self):
        return self.username

    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following_users.count()

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']


class Follow(TimeStampedModel):
    """
    Follow relationship between users.
    """
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_set'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower_set'
    )

    class Meta:
        db_table = 'follows'
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'following']),
        ]

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'


class FriendRequest(TimeStampedModel):
    """
    Friend request between users.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests'
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_friend_requests'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'friend_requests'
        unique_together = ('from_user', 'to_user')
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'{self.from_user.username} -> {self.to_user.username} ({self.status})'
