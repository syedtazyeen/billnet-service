"""
Authentication views for JWT token management.
"""

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from django.conf import settings
from app.core.otp_service import OTPService
from .serializers import SendOTPSerializer, VerifyOTPSerializer


User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing authentication.
    """

    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="send-otp")
    def send_otp(self, request):
        """
        Send OTP to identifier (email or phone).
        """
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]

        result = OTPService.create_and_send_otp(identifier)

        if not result["success"]:
            raise ValidationError("Failed to send OTP. Please try again.")

        return Response(
            {
                "request_id": result["request_id"],
                "identifier": identifier,
                "expires_in": getattr(settings, "OTP_EXPIRY_MINUTES", 5) * 60 * 1000,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="verify-otp")
    def verify_otp(self, request):
        """
        Verify OTP without logging in.
        """
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_id = serializer.validated_data["request_id"]
        otp = serializer.validated_data["otp"]

        # Validate OTP
        validation_result = OTPService.validate_otp(request_id, otp)

        if not validation_result["valid"]:
            raise ValidationError("Invalid OTP")

        return Response(
            {"identifier": validation_result["identifier"]},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request):
        """
        Logout user by blacklisting the refresh token.
        """
        try:
            refresh_token_value = request.data.get("refresh")
            if refresh_token_value:
                token = RefreshToken(refresh_token_value)
                token.blacklist()
            return Response({"message": "Successfully logged out"})
        except TokenError as exc:
            raise ValidationError("Invalid token") from exc

    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh_token(self, request):
        """
        Refresh access token using refresh token.
        """
        try:
            refresh_token_value = request.data.get("refresh")
            if not refresh_token_value:
                raise ValidationError("Refresh token is required")

            token = RefreshToken(refresh_token_value)
            return Response({"access": str(token.access_token)})
        except TokenError as exc:
            raise ValidationError("Invalid refresh token") from exc
