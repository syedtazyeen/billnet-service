"""
Workspace API views
"""

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from apps.workspaces.models.members import WorkspaceMember
from apps.workspaces.api.v1.serializers import UserWorkspaceSerializer


@extend_schema(tags=["Workspaces"])
class WorkspaceViewSet(viewsets.GenericViewSet):
    """
    Workspace API viewset
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["GET"], url_path="my-memberships")
    def get_user_workspaces(self, request):
        """
        Get user membership information for all workspaces
        """
        workspace_members = WorkspaceMember.objects.filter(user=request.user)
        serializer = UserWorkspaceSerializer(workspace_members, many=True)
        return Response(serializer.data)
