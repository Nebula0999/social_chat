"""
Views for chat app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, MessageRead
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for Conversation model."""
    queryset = Conversation.objects.all().prefetch_related('participants')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter conversations for current user."""
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants').order_by('-created_at')

    def create(self, request):
        """Create a new conversation."""
        participant_ids = request.data.get('participant_ids', [])
        conversation_type = request.data.get('conversation_type', 'direct')
        name = request.data.get('name', '')

        # Validate direct message conversations
        if conversation_type == 'direct' and len(participant_ids) != 1:
            return Response(
                {'error': 'Direct conversations must have exactly one other participant.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if direct conversation already exists
        if conversation_type == 'direct':
            other_user_id = participant_ids[0]
            existing_conversation = Conversation.objects.filter(
                conversation_type='direct',
                participants=request.user
            ).filter(
                participants__id=other_user_id
            ).first()

            if existing_conversation:
                serializer = self.get_serializer(existing_conversation)
                return Response(serializer.data)

        # Create new conversation
        conversation = Conversation.objects.create(
            name=name,
            conversation_type=conversation_type
        )
        conversation.participants.add(request.user)

        for participant_id in participant_ids:
            user = get_object_or_404(User, id=participant_id)
            conversation.participants.add(user)

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a conversation."""
        conversation = self.get_object()

        # Verify user is participant
        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not a participant in this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )

        messages = Message.objects.filter(
            conversation=conversation
        ).select_related('sender').order_by('-created_at')

        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in a conversation."""
        conversation = self.get_object()

        # Verify user is participant
        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not a participant in this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(sender=request.user, conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Message model."""
    queryset = Message.objects.all().select_related('sender', 'conversation')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a message as read."""
        message = self.get_object()
        MessageRead.objects.get_or_create(message=message, user=request.user)
        return Response({'message': 'Message marked as read.'}, status=status.HTTP_200_OK)
