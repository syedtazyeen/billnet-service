"""
Authentication serializers for JWT token management.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from app.core.otp_service import OTPService

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that uses email instead of username.
    """

    username_field = "email"

    def validate(self, attrs):
        # Change 'username' to 'email' in the data
        attrs["username"] = attrs.get("email")
        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["email"] = user.email
        token["role"] = user.role
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name

        return token

    def create(self, validated_data):
        # This method is not used for token serializers
        raise NotImplementedError("Token serializers don't support create operations")


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with OTP verification.
    """

    class Meta:
        """
        Meta class for UserRegistrationSerializer.
        """

        model = User
        fields = (
            "email",
            "phone",
            "first_name",
            "last_name",
            "role",
        )
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone": {"required": False},
        }

    def validate_email(self, value):
        """Check if email already exists in the database."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_phone(self, value):
        """Check if phone number already exists in the database."""
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "User with this phone number already exists."
            )
        return value

    def create(self, validated_data):
        """Create user without password for OTP-based auth."""
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    """

    class Meta:
        """
        Meta class for UserProfileSerializer.
        """

        model = User
        fields = (
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "role",
            "status",
            "updated_at",
            "created_at",
        )
        read_only_fields = ("id", "email", "created_at", "updated_at")


class SendOTPSerializer(serializers.Serializer):
    """
    Serializer for sending OTP to identifier.
    """

    identifier = serializers.CharField(
        max_length=255, help_text="Email or phone number"
    )

    def validate_identifier(self, value):
        """Validate if the identifier is a valid email or phone number."""
        if not OTPService.is_valid_identifier(value):
            raise serializers.ValidationError("Invalid email or phone number format.")
        return value

    def create(self, validated_data):
        """Not used for this serializer."""
        raise NotImplementedError("This serializer is for validation only.")

    def update(self, instance, validated_data):
        """Not used for this serializer."""
        raise NotImplementedError("This serializer is for validation only.")


class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying OTP.
    """

    request_id = serializers.CharField(
        max_length=255, help_text="Request ID from send OTP response"
    )
    otp = serializers.CharField(max_length=10, help_text="OTP code")

    def validate_otp(self, value):
        """Validate if the OTP is a valid number."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value

    def create(self, validated_data):
        """Not used for this serializer."""
        raise NotImplementedError("This serializer is for validation only.")

    def update(self, instance, validated_data):
        """Not used for this serializer."""
        raise NotImplementedError("This serializer is for validation only.")


class OTPLoginSerializer(serializers.Serializer):
    """
    Serializer for OTP-based login.
    """

    request_id = serializers.CharField(
        max_length=255, help_text="Request ID from send OTP response"
    )
    otp = serializers.CharField(max_length=10, help_text="OTP code")

    def validate_otp(self, value):
        """Validate if the OTP is a valid number."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value

    def create(self, validated_data):
        """Not used for this serializer."""
        raise NotImplementedError("This serializer is for validation only.")

    def update(self, instance, validated_data):
        """Not used for this serializer."""
        raise NotImplementedError("This serializer is for validation only.")
