"""
Workspaces app config
"""

from django.apps import AppConfig


class WorkspacesConfig(AppConfig):
    """
    Workspaces app config
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.workspaces"
    label = "workspaces"
