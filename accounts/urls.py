"""
URL patterns for accounts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FriendRequestViewSet, UserRegistrationView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'friend-requests', FriendRequestViewSet)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('', include(router.urls)),
]
