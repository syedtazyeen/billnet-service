"""Agents app config."""

from django.apps import AppConfig


class AgentsConfig(AppConfig):
    """Agents app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.agents"
    label = "agents"
