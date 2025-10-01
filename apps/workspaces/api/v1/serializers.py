"""
Workspace API serializers
"""

from rest_framework import serializers
from apps.workspaces.models.workspace import Workspace, WorkspaceMember


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    """Serializer for WorkspaceMember model."""

    class Meta:
        """Meta class for WorkspaceMemberSerializer."""

        model = WorkspaceMember
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class UserWorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for UserWorkspace model - returns member as main object with workspace nested."""

    workspace = serializers.SerializerMethodField()

    class Meta:
        """Meta class for UserWorkspaceSerializer."""

        model = WorkspaceMember
        fields = ["id", "role", "created_at", "updated_at", "workspace"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_workspace(self, obj):
        """Get the workspace information for this member."""
        return {
            "id": str(obj.workspace.id),
            "name": obj.workspace.name,
            "description": obj.workspace.description,
            "created_at": obj.workspace.created_at,
            "updated_at": obj.workspace.updated_at,
        }


class WorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for Workspace model."""

    members = WorkspaceMemberSerializer(many=True, read_only=True)

    class Meta:
        """Meta class for WorkspaceSerializer."""

        model = Workspace
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
