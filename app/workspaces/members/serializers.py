"""
Serializers for WorkspaceMember model.
"""

from rest_framework import serializers
from app.workspaces.members.models import WorkspaceMember

class WorkspaceMemberSerializer(serializers.ModelSerializer):
    """Serializer for WorkspaceMember model."""

    class Meta:
        """Meta class for WorkspaceMemberSerializer."""

        model = WorkspaceMember
        fields = "__all__"
