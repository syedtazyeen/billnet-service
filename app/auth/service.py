"""
Authentication service for handling complex authentication logic.
"""

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import ValidationError
from app.core.otp_service import OTPService
from app.workspaces.models import Workspace

User = get_user_model()


class AuthService:
    """
    Service for authentication operations.
    """

    def send_otp(self, identifier):
        """
        Send OTP to identifier (email or phone).
        """
        return OTPService.create_and_send_otp(identifier)

    def verify_otp(self, identifier, request_id, otp):
        """
        Verify OTP and authenticate user (create if new, login if existing).
        """
        # Validate OTP
        is_valid = OTPService.validate_otp(identifier, request_id, otp)

        if not is_valid:
            raise ValidationError("Invalid OTP")

        # Find or create user
        user, is_new_user = self._find_or_create_user(identifier)
        if not user:
            raise ValidationError("Failed to create user")

        # Create workspace
        if is_new_user:
            Workspace.objects.create(
                name=f"{user.first_name}'s Workspace",
                created_by=user,
            )

        # Generate JWT tokens
        token_result = self._generate_jwt_tokens(user)
        if not token_result:
            raise ValidationError("Failed to generate JWT tokens")

        return {
            "access_token": token_result[0],
            "refresh_token": token_result[1],
            "user": user,
            "is_new_user": is_new_user,
        }

    def logout(self, refresh_token_value):
        """
        Logout user by blacklisting the refresh token.
        """
        try:
            if refresh_token_value:
                token = RefreshToken(refresh_token_value)
                token.blacklist()
            return True
        except TokenError as exc:
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
