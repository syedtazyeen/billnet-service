"""
Authentication views for JWT token management.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.conf import settings
from .service import AuthService
from .serializers import SendOTPSerializer, VerifyOTPSerializer, UserProfileSerializer


User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing authentication.
    """

    permission_classes = [AllowAny]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_service = AuthService()

    @action(detail=False, methods=["post"], url_path="send-otp")
    def send_otp(self, request):
        """
        Send OTP to identifier (email or phone).
        """
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        result = self.auth_service.send_otp(identifier)

        return Response(
            {
                "request_id": result["request_id"],
                "identifier": identifier,
                "expires_in": settings.OTP_EXPIRY_MINUTES * 60 * 1000,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="verify-otp")
    def verify_otp(self, request):
        """
        Verify OTP and authenticate user (create if new, login if existing).
        """
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        request_id = serializer.validated_data["request_id"]
        otp = serializer.validated_data["otp"]

        result = self.auth_service.verify_otp(identifier, request_id, otp)

        return Response(
            {
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "user": UserProfileSerializer(result["user"]).data,
                "is_new_user": result["is_new_user"],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request):
        """
        Logout user by blacklisting the refresh token.
        """
        refresh_token_value = request.data.get("refresh")
        self.auth_service.logout(refresh_token_value)

        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh_token(self, request):
        """
        Refresh access token using refresh token.
        """
        refresh_token_value = request.data.get("refresh")
        access_token = self.auth_service.refresh_token(refresh_token_value)

        return Response({"access_token": access_token}, status=status.HTTP_200_OK)
