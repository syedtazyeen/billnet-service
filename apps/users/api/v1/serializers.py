"""
Serializers for User model.
"""

from typing import Any, Dict
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.users.models import User


class BaseUserSerializer(serializers.ModelSerializer):
    """Base serializer with common user fields."""

    social_links = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        validators=[],
    )
    preferences = serializers.DictField(
        required=False,
        allow_null=True,
        validators=[],
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "status",
            "avatar",
            "bio",
            "social_links",
            "preferences",
            "created_at",
            "updated_at",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_active"]


def validate_social_links(value: Dict[str, Any]) -> Dict[str, Any]:
    """Validate social links format."""

    if not isinstance(value, dict):
        raise serializers.ValidationError("Social links must be a dictionary.")

    valid_platforms = {
        "website",
        "github",
        "linkedin",
        "x",
        "facebook",
        "instagram",
        "youtube",
        "discord",
        "telegram",
    }

    for platform, username in value.items():
        if platform not in valid_platforms:
            raise serializers.ValidationError(
                f"Invalid platform '{platform}'. Valid platforms are: {', '.join(valid_platforms)}"
            )
        if not isinstance(username, str) or not username.strip():
            raise serializers.ValidationError(f"Invalid username for {platform}. Must be a non-empty string.")
        if platform == "website" and not username.startswith(("http://", "https://")):
            raise serializers.ValidationError("Website must be a valid HTTP/HTTPS URL.")
    return value


def validate_preferences(value: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user preference settings."""

    if not isinstance(value, dict):
        raise serializers.ValidationError("Preferences must be a dictionary.")

    valid_themes = {"light", "dark", "auto"}
    valid_languages = {"en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi"}

    if "theme" in value and value["theme"] not in valid_themes:
        raise serializers.ValidationError(f"Invalid theme. Valid themes are: {', '.join(valid_themes)}")

    if "language" in value and value["language"] not in valid_languages:
        raise serializers.ValidationError(f"Invalid language. Valid languages are: {', '.join(valid_languages)}")

    notification_keys = {
        "email_notifications",
        "push_notifications",
        "marketing_emails",
    }

    for key in notification_keys:
        if key in value and not isinstance(value[key], bool):
            raise serializers.ValidationError(f"{key} must be a boolean value.")

    return value


class UserSerializer(BaseUserSerializer):
    """Serializer for User model with validations for social_links & preferences."""

    social_links = serializers.DictField(required=False, allow_null=True, validators=[validate_social_links])
    preferences = serializers.DictField(required=False, allow_null=True, validators=[validate_preferences])


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users with password validation."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        """Meta class for UserCreateSerializer."""

        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "role",
            "password",
            "password_confirm",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(BaseUserSerializer):
    """Serializer for updating user information (partial update allowed)."""

    social_links = serializers.DictField(required=False, allow_null=True, validators=[validate_social_links])
    preferences = serializers.DictField(required=False, allow_null=True, validators=[validate_preferences])

    class Meta(BaseUserSerializer.Meta):
        """Meta class for UserUpdateSerializer."""

        fields = [
            "email",
            "first_name",
            "last_name",
            "role",
            "status",
            "avatar",
            "bio",
            "social_links",
            "preferences",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }


class UserProfileSerializer(BaseUserSerializer):
    """Read-only serializer for user profile information."""

    social_links = serializers.DictField(read_only=True)
    preferences = serializers.DictField(read_only=True)

    class Meta(BaseUserSerializer.Meta):
        """Meta class for UserProfileSerializer."""

        read_only_fields = BaseUserSerializer.Meta.read_only_fields + [
            "email",
            "role",
            "status",
        ]
