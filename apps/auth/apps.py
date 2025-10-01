"""Auth app config"""

from django.apps import AppConfig


class AuthConfig(AppConfig):
    """Auth app config"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auth"
    label = "custom_auth"
