"""
Views for posts app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Post, Like, Comment
from .serializers import PostSerializer, LikeSerializer, CommentSerializer
from accounts.models import Follow


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet for Post model."""
    queryset = Post.objects.all().select_related('author').prefetch_related('likes')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter posts based on query params."""
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(author_id=user_id)
        return queryset

    def perform_create(self, serializer):
        """Set author to current user."""
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Get personalized feed for current user."""
        # Get users that the current user follows
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)

        # Get posts from followed users and own posts
        posts = Post.objects.filter(
            Q(author_id__in=following_ids) | Q(author=request.user)
        ).select_related('author').prefetch_related('likes').order_by('-created_at')

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a post."""
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            return Response(
                {'error': 'You have already liked this post.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'message': 'Post liked successfully.'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        """Unlike a post."""
        post = self.get_object()
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()

        if not deleted:
            return Response(
                {'error': 'You have not liked this post.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'message': 'Post unliked successfully.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def repost(self, request, pk=None):
        """Repost a post."""
        original_post = self.get_object()
        repost = Post.objects.create(
            author=request.user,
            content=request.data.get('content', ''),
            repost_of=original_post
        )
        serializer = self.get_serializer(repost)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get comments for a post."""
        post = self.get_object()
        comments = Comment.objects.filter(post=post, parent=None).select_related('author')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment model."""
    queryset = Comment.objects.all().select_related('author', 'post')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Set author to current user."""
        serializer.save(author=self.request.user)
