"""
Views for accounts app.
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Follow, FriendRequest
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    FollowSerializer,
    FriendRequestSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """Follow a user."""
        user_to_follow = self.get_object()
        if user_to_follow == request.user:
            return Response(
                {'error': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

        if not created:
            return Response(
                {'error': 'You are already following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'message': f'You are now following {user_to_follow.username}.'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        """Unfollow a user."""
        user_to_unfollow = self.get_object()
        deleted, _ = Follow.objects.filter(
            follower=request.user,
            following=user_to_unfollow
        ).delete()

        if not deleted:
            return Response(
                {'error': 'You are not following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'message': f'You have unfollowed {user_to_unfollow.username}.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        """Get user's followers."""
        user = self.get_object()
        followers = Follow.objects.filter(following=user)
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        """Get users that this user is following."""
        user = self.get_object()
        following = Follow.objects.filter(follower=user)
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)


class FriendRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for FriendRequest model."""
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter friend requests for current user."""
        return FriendRequest.objects.filter(
            to_user=self.request.user,
            status='pending'
        )

    def create(self, request):
        """Send a friend request."""
        to_user_id = request.data.get('to_user_id')
        to_user = get_object_or_404(User, id=to_user_id)

        if to_user == request.user:
            return Response(
                {'error': 'You cannot send a friend request to yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        friend_request, created = FriendRequest.objects.get_or_create(
            from_user=request.user,
            to_user=to_user,
            defaults={'status': 'pending'}
        )

        if not created:
            return Response(
                {'error': 'Friend request already sent.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a friend request."""
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response(
                {'error': 'You cannot accept this friend request.'},
                status=status.HTTP_403_FORBIDDEN
            )

        friend_request.status = 'accepted'
        friend_request.save()

        # Auto-follow each other when friend request is accepted
        Follow.objects.get_or_create(
            follower=friend_request.from_user,
            following=friend_request.to_user
        )
        Follow.objects.get_or_create(
            follower=friend_request.to_user,
            following=friend_request.from_user
        )

        return Response(
            {'message': 'Friend request accepted.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a friend request."""
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response(
                {'error': 'You cannot reject this friend request.'},
                status=status.HTTP_403_FORBIDDEN
            )

        friend_request.status = 'rejected'
        friend_request.save()

        return Response(
            {'message': 'Friend request rejected.'},
            status=status.HTTP_200_OK
        )
