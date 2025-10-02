"""
Workspace Permissions with Role-Based Access Control
"""

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission
from apps.workspaces.models.roles import WorkspaceRole, WorkspaceRoleType


class HasWorkspaceRole(BasePermission):
    """
    Allows access only if the user has one of the specified roles
    in the current workspace.

    Usage:
        permission_classes = [HasWorkspaceRole(roles=["owner", "member"])]

    Pass roles as a list of strings representing allowed roles.
    """

    def __init__(self, roles=None):
        if roles is None:
            roles = []
        self.allowed_roles = set(roles)

    def has_permission(self, request, view):
        workspace_id = view.kwargs.get("workspace_id")
        if not workspace_id:
            return False

        try:
            # Get the user's role in the workspace
            workspace_role = WorkspaceRole.objects.get(user=request.user, workspace_id=workspace_id)
            # Check if the user's role is in the allowed roles
            return workspace_role.type in self.allowed_roles
        except ObjectDoesNotExist:
            return False


class IsWorkspaceMember(HasWorkspaceRole):
    """
    Checks if user is any member (has any role) in the workspace.
    """

    def __init__(self):
        # Allow any role type (owner or member)
        super().__init__(roles=[WorkspaceRoleType.OWNER, WorkspaceRoleType.MEMBER])


class IsWorkspaceOwner(HasWorkspaceRole):
    """
    Checks if user has the owner role in the workspace.
    """

    def __init__(self):
        super().__init__(roles=[WorkspaceRoleType.OWNER])
