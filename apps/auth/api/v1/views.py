"""
AuthViewSet for managing authentication.
"""

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from apps.auth.api.v1.serializers import SendCodeSerializer, VerifyCodeSerializer
from apps.auth.service import AuthService
from apps.core.services.otp import OTPService
from apps.core.services.email import EmailService


@extend_schema(tags=["Auth"])
class AuthViewSet(viewsets.GenericViewSet):
    """
    AuthViewSet for managing authentication.
    """

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthService(otp_service=OTPService(email_service=EmailService()))

    @action(detail=False, methods=["post"], url_path="send-code")
    def send_code(self, request):
        """
        Send a code to the user.
        """
        serializer = SendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = self.auth_service.send_code(serializer.validated_data["identifier"])

        return Response({"request_id": result.request_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="verify-code")
    def verify_code(self, request):
        """
        Verify a code.
        """
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = self.auth_service.verify_code(
            request_id=serializer.validated_data["request_id"],
            identifier=serializer.validated_data["identifier"],
            code=serializer.validated_data["code"],
        )

        return Response(
            {
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "is_new_user": result["is_new_user"],
            },
            status=status.HTTP_200_OK,
        )
