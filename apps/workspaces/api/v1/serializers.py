"""
Workspace API serializers
"""

from rest_framework import serializers
from apps.workspaces.models.workspace import Workspace, WorkspaceRole


class WorkspaceRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for WorkspaceRole model.
    Optionally includes nested workspace details.
    """

    workspace = serializers.SerializerMethodField()

    class Meta:
        """Meta class for WorkspaceRoleSerializer."""
        model = WorkspaceRole
        fields = ["id", "type", "created_at", "updated_at", "workspace"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        """
        Accept custom argument `include_workspace` (default False)
        to control nested workspace serialization detail.
        """
        self.include_workspace = kwargs.pop("include_workspace", False)
        super().__init__(*args, **kwargs)

    def get_workspace(self, obj):
        """Get the workspace for this role."""
        if not self.include_workspace:
            # Return only workspace ID if not including full details.
            return str(obj.workspace.id)

        # Full workspace details
        return {
            "id": str(obj.workspace.id),
            "name": obj.workspace.name,
            "description": obj.workspace.description,
            "created_at": obj.workspace.created_at,
            "updated_at": obj.workspace.updated_at,
        }


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Serializer for Workspace model.
    Optionally includes all member roles.
    """

    roles = serializers.SerializerMethodField()

    class Meta:
        """Meta class for WorkspaceSerializer."""
        model = Workspace
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        """
        Accept custom argument `include_roles` (default False)
        to control whether roles data is included.
        """
        self.include_roles = kwargs.pop("include_roles", False)
        super().__init__(*args, **kwargs)

    def get_roles(self, obj):
        """Get the roles for this workspace if requested."""
        if not self.include_roles:
            return None
        roles = WorkspaceRole.objects.filter(workspace=obj)
        serializer = WorkspaceRoleSerializer(roles, many=True, context=self.context)
        return serializer.data
