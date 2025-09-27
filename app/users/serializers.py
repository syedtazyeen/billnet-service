"""Serializers for User model."""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with custom fields."""

    class Meta:
        """Meta class for UserSerializer."""

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
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""

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

    def validate(self, attrs):
        """Validate that password and password_confirm match."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        """Create a new user with hashed password."""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""

    class Meta:
        """Meta class for UserUpdateSerializer."""

        model = User
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


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information (read-only for users)."""

    class Meta:
        """Meta class for UserProfileSerializer."""

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
        read_only_fields = [
            "id",
            "email",
            "role",
            "status",
            "created_at",
            "updated_at",
            "is_active",
        ]


def validate_social_links(value):
    """Validate social links format."""
    if not isinstance(value, dict):
        raise serializers.ValidationError("Social links must be a dictionary.")

    valid_platforms = [
        "website",
        "github",
        "linkedin",
        "x",
        "facebook",
        "instagram",
        "youtube",
        "discord",
        "telegram",
    ]

    for platform, username in value.items():
        if platform not in valid_platforms:
            raise serializers.ValidationError(
                f"Invalid platform '{platform}'. Valid platforms are: {', '.join(valid_platforms)}"
            )
        if not isinstance(username, str) or len(username.strip()) == 0:
            raise serializers.ValidationError(
                f"Invalid username for {platform}. Must be a non-empty string."
            )
        # For website, allow full URLs
        if platform == "website" and not username.startswith(("http://", "https://")):
            raise serializers.ValidationError("Website must be a valid HTTP/HTTPS URL.")

    return value


def validate_preferences(value):
    """Validate preferences format."""
    if not isinstance(value, dict):
        raise serializers.ValidationError("Preferences must be a dictionary.")

    valid_themes = ["light", "dark", "auto"]
    valid_languages = [
        "en",
        "es",
        "fr",
        "de",
        "it",
        "pt",
        "ru",
        "zh",
        "ja",
        "ko",
        "ar",
        "hi",
    ]

    if "theme" in value and value["theme"] not in valid_themes:
        raise serializers.ValidationError(
            f"Invalid theme. Valid themes are: {', '.join(valid_themes)}"
        )

    if "language" in value and value["language"] not in valid_languages:
        raise serializers.ValidationError(
            f"Invalid language. Valid languages are: {', '.join(valid_languages)}"
        )

    # Validate notification settings are boolean
    notification_keys = [
        "email_notifications",
        "push_notifications",
        "marketing_emails",
    ]
    for key in notification_keys:
        if key in value and not isinstance(value[key], bool):
            raise serializers.ValidationError(f"{key} must be a boolean value.")

    return value


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile with validation."""

    social_links = serializers.JSONField(
        validators=[validate_social_links], required=False
    )
    preferences = serializers.JSONField(
        validators=[validate_preferences], required=False
    )

    class Meta:
        """Meta class for UserProfileUpdateSerializer."""

        model = User
        fields = [
            "first_name",
            "last_name",
            "avatar",
            "bio",
            "social_links",
            "preferences",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }
