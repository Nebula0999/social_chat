"""
Tests for posts app.
"""
import pytest
from django.contrib.auth import get_user_model
from posts.models import Post, Like, Comment

User = get_user_model()


@pytest.mark.django_db
class TestPostModel:
    def test_create_post(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
        post = Post.objects.create(author=user, content='Test post content')

        assert post.author == user
        assert post.content == 'Test post content'
        assert post.like_count == 0
        assert post.comment_count == 0

    def test_like_post(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
        post = Post.objects.create(author=user, content='Test post')

        like = Like.objects.create(user=user, post=post)

        assert like.user == user
        assert like.post == post
        assert post.like_count == 1

    def test_comment_on_post(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
        post = Post.objects.create(author=user, content='Test post')

        comment = Comment.objects.create(author=user, post=post, content='Test comment')

        assert comment.author == user
        assert comment.post == post
        assert comment.content == 'Test comment'
        assert post.comment_count == 1
