"""
GraphQL schema for social_network project.
"""
import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from django.contrib.auth import get_user_model
from accounts.models import Follow, FriendRequest
from posts.models import Post, Like, Comment
from chat.models import Conversation, Message
from notifications.models import Notification

User = get_user_model()


# Object Types
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'bio', 'avatar', 'date_joined')


class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
        fields = '__all__'


class FriendRequestType(DjangoObjectType):
    class Meta:
        model = FriendRequest
        fields = '__all__'


class PostType(DjangoObjectType):
    like_count = graphene.Int()
    comment_count = graphene.Int()

    class Meta:
        model = Post
        fields = '__all__'

    def resolve_like_count(self, info):
        return self.like_count

    def resolve_comment_count(self, info):
        return self.comment_count


class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = '__all__'


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = '__all__'


class ConversationType(DjangoObjectType):
    class Meta:
        model = Conversation
        fields = '__all__'


class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = '__all__'


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = '__all__'


# Query
class Query(graphene.ObjectType):
    # User queries
    me = graphene.Field(UserType)
    users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.ID(required=True))

    # Post queries
    feed = graphene.List(PostType)
    posts = graphene.List(PostType, user_id=graphene.ID())
    post = graphene.Field(PostType, id=graphene.ID(required=True))

    # Chat queries
    conversations = graphene.List(ConversationType)
    conversation = graphene.Field(ConversationType, id=graphene.ID(required=True))
    messages = graphene.List(MessageType, conversation_id=graphene.ID(required=True))

    # Notification queries
    notifications = graphene.List(NotificationType)
    unread_notifications = graphene.List(NotificationType)

    @login_required
    def resolve_me(self, info):
        return info.context.user

    @login_required
    def resolve_users(self, info):
        return User.objects.all()

    @login_required
    def resolve_user(self, info, id):
        return User.objects.get(pk=id)

    @login_required
    def resolve_feed(self, info):
        user = info.context.user
        following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
        return Post.objects.filter(author_id__in=list(following_ids) + [user.id]).order_by('-created_at')

    @login_required
    def resolve_posts(self, info, user_id=None):
        if user_id:
            return Post.objects.filter(author_id=user_id).order_by('-created_at')
        return Post.objects.all().order_by('-created_at')

    @login_required
    def resolve_post(self, info, id):
        return Post.objects.get(pk=id)

    @login_required
    def resolve_conversations(self, info):
        return Conversation.objects.filter(participants=info.context.user)

    @login_required
    def resolve_conversation(self, info, id):
        return Conversation.objects.get(pk=id)

    @login_required
    def resolve_messages(self, info, conversation_id):
        return Message.objects.filter(conversation_id=conversation_id).order_by('-created_at')

    @login_required
    def resolve_notifications(self, info):
        return Notification.objects.filter(recipient=info.context.user).order_by('-created_at')

    @login_required
    def resolve_unread_notifications(self, info):
        return Notification.objects.filter(recipient=info.context.user, is_read=False).order_by('-created_at')


# Mutations
class RegisterInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    first_name = graphene.String()
    last_name = graphene.String()


class AuthPayload(graphene.ObjectType):
    user = graphene.Field(UserType)
    token = graphene.String()


class Register(graphene.Mutation):
    class Arguments:
        input = RegisterInput(required=True)

    Output = AuthPayload

    def mutate(self, info, input):
        user = User.objects.create_user(
            username=input.username,
            email=input.email,
            password=input.password,
            first_name=input.get('first_name', ''),
            last_name=input.get('last_name', '')
        )
        return AuthPayload(user=user, token='use-jwt-token-here')


class CreatePostInput(graphene.InputObjectType):
    content = graphene.String(required=True)


class CreatePost(graphene.Mutation):
    class Arguments:
        input = CreatePostInput(required=True)

    post = graphene.Field(PostType)

    @login_required
    def mutate(self, info, input):
        post = Post.objects.create(
            author=info.context.user,
            content=input.content
        )
        return CreatePost(post=post)


class FollowUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, user_id):
        user_to_follow = User.objects.get(pk=user_id)
        if user_to_follow == info.context.user:
            return FollowUser(success=False, message='You cannot follow yourself.')

        follow, created = Follow.objects.get_or_create(
            follower=info.context.user,
            following=user_to_follow
        )

        if not created:
            return FollowUser(success=False, message='Already following this user.')

        return FollowUser(success=True, message='Successfully followed user.')


class SendMessageInput(graphene.InputObjectType):
    conversation_id = graphene.ID(required=True)
    content = graphene.String(required=True)


class SendMessage(graphene.Mutation):
    class Arguments:
        input = SendMessageInput(required=True)

    message = graphene.Field(MessageType)

    @login_required
    def mutate(self, info, input):
        conversation = Conversation.objects.get(pk=input.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=info.context.user,
            content=input.content
        )
        return SendMessage(message=message)


class MarkMessageRead(graphene.Mutation):
    class Arguments:
        message_id = graphene.ID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, message_id):
        message = Message.objects.get(pk=message_id)
        from chat.models import MessageRead
        MessageRead.objects.get_or_create(message=message, user=info.context.user)
        return MarkMessageRead(success=True)


class Mutation(graphene.ObjectType):
    register = Register.Field()
    create_post = CreatePost.Field()
    follow_user = FollowUser.Field()
    send_message = SendMessage.Field()
    mark_message_read = MarkMessageRead.Field()


# Subscriptions (basic structure - requires additional setup for real-time)
class Subscription(graphene.ObjectType):
    message_sent = graphene.Field(MessageType, conversation_id=graphene.ID(required=True))
    new_notification = graphene.Field(NotificationType)


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
