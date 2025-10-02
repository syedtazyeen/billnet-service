"""
Invoices app config
"""

from django.apps import AppConfig


class InvoicesConfig(AppConfig):
    """
    Invoices app config
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.invoices"
    label = "invoices"
