"""
URL patterns for posts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
