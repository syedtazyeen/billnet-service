"""
Workspace permissions
"""

from rest_framework.permissions import BasePermission

class IsWorkspaceMember(BasePermission):
    """
    Permission to check if the user is a member of the workspace
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_workspace_member