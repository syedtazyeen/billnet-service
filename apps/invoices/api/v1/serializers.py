"""
Invoice serializers
"""

from rest_framework import serializers
from apps.invoices.models import Invoice
from apps.users.api.v1.serializers import UserSimpleSerializer
from apps.workspaces.models import Workspace


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Invoice serializer with optional nested user representation for created_by.
    """

    created_by = serializers.SerializerMethodField()

    class Meta:
        """Meta class for InvoiceSerializer."""

        model = Invoice
        fields = [
            "id",
            "description",
            "amount",
            "status",
            "type",
            "due_date",
            "paid_date",
            "file_url",
            "created_at",
            "updated_at",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]

    def __init__(self, *args, include_user=False, **kwargs):
        """
        Optionally include serialized user data for created_by.
        Default: Only user ID.
        """
        self.include_user = include_user
        super().__init__(*args, **kwargs)

    def get_created_by(self, obj):
        """Get the created_by user."""
        if self.include_user:
            # Return user detail serialization
            return UserSimpleSerializer(obj.created_by, context=self.context).data
        else:
            # Return only user id
            return obj.created_by_id

    def create(self, validated_data):
        """Create an invoice."""
        workspace_id = self.context.get("workspace_id")
        created_by = self.context.get("created_by")

        if not workspace_id or not created_by:
            raise serializers.ValidationError("workspace_id and created_by must be set.")

        workspace = Workspace.objects.get(id=workspace_id)
        if not workspace:
            raise serializers.ValidationError("Workspace not found.")

        validated_data["workspace"] = workspace
        validated_data["created_by"] = created_by

        return super().create(validated_data)
