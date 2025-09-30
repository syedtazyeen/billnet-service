"""
ViewSet for managing users.
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import User
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserProfileSerializer,
)


class UserViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing users.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        serializers = {
            "create": UserCreateSerializer,
            "update": UserUpdateSerializer,
            "partial_update": UserUpdateSerializer,
            "profile": UserProfileSerializer,
            "update_profile": UserProfileSerializer,
        }
        return serializers.get(self.action, UserSerializer)

    def get_permissions(self):
        """Set permissions based on action."""
        permissions_map = {
            "create": [IsAdminUser],
            "update": [IsAuthenticated],
            "partial_update": [IsAuthenticated],
            "profile": [IsAuthenticated],
            "update_profile": [IsAuthenticated],
        }
        permissions = permissions_map.get(self.action, [IsAuthenticated])
        return [permission() for permission in permissions]

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        querysets = {
            "admin": User.objects.all(),
            "user": User.objects.filter(status="active"),
        }
        queryset = querysets.get(self.request.user.role, User.objects.all())
        return queryset

    @action(detail=False, methods=["get"], url_path="me")
    def profile(self, request):
        """Get current user's profile."""
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, methods=["patch"], url_path="me")
    def update_profile(self, request):
        """Update current user's profile."""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
