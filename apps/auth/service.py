"""
Service for managing authentication.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import ValidationError
from apps.core.services.otp import OTPService
from apps.users.models import User


logger = logging.getLogger(__name__)


@dataclass
class OTPResult:
    """
    Result object for OTP operations.
    """

    request_id: Optional[str]
    success: bool
    message: str


class AuthService:
    """
    Service orchestrating authentication.
    """

    def __init__(self, otp_service: OTPService):
        self.otp_service = otp_service

    def _generate_jwt_tokens(self, user):
        """
        Generate JWT tokens for user.
        """
        try:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Add claims to token
            if user.email:
                access_token["email"] = user.email
            if user.phone:
                access_token["phone"] = user.phone

            return str(access_token), str(refresh)
        except (AttributeError, TypeError) as exc:
            raise exc

    def _find_or_create_user(self, identifier):
        """
        Find existing user or create new user based on identifier.
        """
        user = None
        is_new_user = False

        # Check if user exists
        if "@" in identifier:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                pass
        else:
            try:
                user = User.objects.get(phone=identifier)
            except User.DoesNotExist:
                pass

        # Create user if doesn't exist
        if not user:
            is_new_user = True
            try:
                user = User.objects.create_user(identifier=identifier)
            except (ValueError, TypeError) as exc:
                raise exc

        return user, is_new_user

    def send_code(self, identifier: str) -> OTPResult:
        """
        Send an OTP verification code to the specified identifier.
        """
        try:
            self.otp_service.get_identifier_type_or_raise(identifier)
        except ValidationError as ve:
            logger.warning("send_code validation failed: %s", ve)
            return OTPResult(request_id=None, success=False, message=str(ve))
        except Exception as e:
            logger.error("send_code unexpected error: %s", e, exc_info=True)
            return OTPResult(request_id=None, success=False, message="Unexpected error")

        try:
            result = self.otp_service.create_and_send_otp(identifier)
            request_id = result.get("request_id") if result else None
            if request_id:
                return OTPResult(request_id=request_id, success=True, message="OTP sent")
            else:
                return OTPResult(request_id=None, success=False, message="Failed to generate OTP")
        except Exception as e:
            logger.error("send_code failed to create/send OTP: %s", e, exc_info=True)
            return OTPResult(request_id=None, success=False, message="Internal error sending OTP")

    def verify_code(self, identifier: str, request_id: str, code: str):
        """
        Verify an OTP code provided by the user.
        """
        try:
            is_valid = self.otp_service.validate_otp(identifier, request_id, code)
            if not is_valid:
                raise ValidationError("Invalid verification code")
            user, is_new_user = self._find_or_create_user(identifier)
            access_token, refresh_token = self._generate_jwt_tokens(user)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "is_new_user": is_new_user,
            }
        except Exception as exc:
            logger.error("verify_code error validating OTP: %s", exc, exc_info=True)
            raise exc

    def refresh_token(self, refresh_token_value):
        """
        Refresh access token using refresh token.
        """
        try:
            if not refresh_token_value:
                raise ValidationError("Refresh token is required")

            token = RefreshToken(refresh_token_value)
            return str(token.access_token)
        except TokenError as exc:
            raise ValidationError("Invalid refresh token") from exc
        except Exception as exc:
            logger.error("refresh_token error: %s", exc, exc_info=True)
            raise exc
