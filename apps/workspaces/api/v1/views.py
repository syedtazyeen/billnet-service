"""
Workspace API views
"""

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from apps.workspaces.permissions import IsWorkspaceMember
from apps.workspaces.models.roles import WorkspaceRole
from apps.workspaces.api.v1.serializers import WorkspaceRoleSerializer


@extend_schema(tags=["Workspaces"])
class UserWorkspaceViewSet(viewsets.GenericViewSet):
    """
    ViewSet for retrieving workspace roles of the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["GET"], url_path="my-roles")
    def get_user_roles(self, request):
        """
        Retrieve all workspace roles assigned to the current user.
        """
        workspace_roles = WorkspaceRole.objects.filter(user=request.user)
        serializer = WorkspaceRoleSerializer(
            workspace_roles, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)


@extend_schema(tags=["Workspaces"])
class WorkspaceViewSet(viewsets.GenericViewSet):
    """
    ViewSet for workspace-related actions.
    """

    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["GET"],
        url_path=r"(?P<workspace_id>[0-9a-f-]{36})/roles",
        permission_classes=[IsWorkspaceMember],
    )
    def get_workspace_roles(self, request, workspace_id=None):
        """
        Retrieve all roles within a given workspace.
        Requires the user to be a member of the workspace.
        """

        roles_qs = WorkspaceRole.objects.filter(workspace_id=workspace_id)
        serializer = WorkspaceRoleSerializer(
            roles_qs, many=True, include_workspace=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)
