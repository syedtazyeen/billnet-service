"""
ViewSet for managing users.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.users.api.v1.serializers import UserProfileSerializer, UserUpdateSerializer


@extend_schema(tags=["Users"])
class UserViewSet(viewsets.GenericViewSet):
    """
    UserViewSet for managing users.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="me")
    def get_user(self, request):
        """Retrieve the authenticated user's profile."""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["patch"], url_path="me")
    def update_user(self, request):
        """Partially update the authenticated user's profile."""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
