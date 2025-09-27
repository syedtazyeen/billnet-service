"""
User model.
"""

import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
)


class UserStatus(models.TextChoices):
    """
    User status choices.
    """

    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"


class UserRole(models.TextChoices):
    """
    User role choices.
    """

    USER = "user", "User"
    ADMIN = "admin", "Admin"


class SocialLinkType(models.TextChoices):
    """
    Social link type choices.
    """

    WEBSITE = "website", "Website"
    LINKEDIN = "linkedin", "LinkedIn"
    TWITTER = "twitter", "Twitter"
    INSTAGRAM = "instagram", "Instagram"
    YOUTUBE = "youtube", "YouTube"
    DISCORD = "discord", "Discord"


class Theme(models.TextChoices):
    """
    Theme choices.
    """

    LIGHT = "light", "Light"
    DARK = "dark", "Dark"
    AUTO = "auto", "Auto"


class Language(models.TextChoices):
    """
    Language choices.
    """

    ENGLISH = "en", "English"
    SPANISH = "es", "Spanish"
    ARABIC = "ar", "Arabic"
    HINDI = "hi", "Hindi"


class UserManager(BaseUserManager):
    """
    Custom user manager for the User model.
    """

    def create_user(self, identifier, password=None, **extra_fields):
        """
        Create and return a regular user.
        """
        if not identifier:
            raise ValueError("The Identifier field must be set")

        if "@" in identifier:
            email = self.normalize_email(identifier)
            phone = None
        else:
            email = None
            phone = identifier

        user = self.model(email=email, phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    User model.
    """

    # Basic user fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        help_text="Phone number for OTP authentication",
    )
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.USER,
        help_text="User role in the system",
    )

    status = models.CharField(
        max_length=10,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
        help_text="Current status of the user account",
    )

    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, help_text="User profile picture"
    )

    bio = models.TextField(
        blank=True, null=True, max_length=500, help_text="User biography or description"
    )

    social_links = models.JSONField(
        default=dict,
        blank=True,
        help_text="Social media usernames",
    )

    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User preferences",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Set email as the username field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    # Custom manager
    objects = UserManager()

    class Meta:
        """Meta class for the User model."""

        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def is_active(self):
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE

    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN

    def get_social_link(self, platform):
        """Get a specific social username by platform."""
        return self.social_links.get(platform)

    def set_social_link(self, platform, username):
        """Set a social username for a specific platform."""
        if not hasattr(self, "social_links") or self.social_links is None:
            self.social_links = {}

        # Validate platform is a valid SocialLinkType
        if platform not in [choice[0] for choice in SocialLinkType.choices]:
            raise ValueError(f"Invalid social platform: {platform}")

        self.social_links[platform] = username

    def remove_social_link(self, platform):
        """Remove a social username for a specific platform."""
        if (
            hasattr(self, "social_links")
            and self.social_links
            and platform in self.social_links
        ):
            del self.social_links[platform]

    def get_preference(self, key, default=None):
        """Get a specific preference value."""
        return self.preferences.get(key, default)

    def set_preference(self, key, value):
        """Set a preference value."""
        if not hasattr(self, "preferences") or self.preferences is None:
            self.preferences = {}

        # Validate theme and language values
        if key == "theme" and value not in [choice[0] for choice in Theme.choices]:
            raise ValueError(f"Invalid theme: {value}")

        if key == "language" and value not in [
            choice[0] for choice in Language.choices
        ]:
            raise ValueError(f"Invalid language: {value}")

        self.preferences[key] = value

    def get_theme(self):
        """Get user's theme preference."""
        return self.get_preference("theme", Theme.AUTO)

    def get_language(self):
        """Get user's language preference."""
        return self.get_preference("language", Language.ENGLISH)

    def set_theme(self, theme):
        """Set user's theme preference."""
        self.set_preference("theme", theme)

    def set_language(self, language):
        """Set user's language preference."""
        self.set_preference("language", language)

    def get_available_social_platforms(self):
        """Get list of available social platforms."""
        return [choice[0] for choice in SocialLinkType.choices]

    def get_available_themes(self):
        """Get list of available themes."""
        return [choice[0] for choice in Theme.choices]

    def get_available_languages(self):
        """Get list of available languages."""
        return [choice[0] for choice in Language.choices]
