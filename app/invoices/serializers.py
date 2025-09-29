"""Serializers for Invoice model."""

from rest_framework import serializers
from app.invoices.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""

    class Meta:
        """Meta class for InvoiceSerializer."""

        model = Invoice
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "created_by": {"read_only": True},
            "updated_by": {"read_only": True},
        }
