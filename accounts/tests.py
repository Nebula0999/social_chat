"""
Tests for accounts app.
"""
import pytest
from django.contrib.auth import get_user_model
from accounts.models import Follow, FriendRequest

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')

    def test_user_str(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert str(user) == 'testuser'


@pytest.mark.django_db
class TestFollowModel:
    def test_follow_user(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass')
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass')

        follow = Follow.objects.create(follower=user1, following=user2)

        assert follow.follower == user1
        assert follow.following == user2
        assert str(follow) == 'user1 follows user2'


@pytest.mark.django_db
class TestFriendRequestModel:
    def test_friend_request(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass')
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass')

        friend_request = FriendRequest.objects.create(from_user=user1, to_user=user2)

        assert friend_request.from_user == user1
        assert friend_request.to_user == user2
        assert friend_request.status == 'pending'
