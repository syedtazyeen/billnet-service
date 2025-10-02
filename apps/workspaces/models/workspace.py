"""
Workspace models
"""

import uuid
from django.db import models, transaction
from apps.workspaces.models.roles import WorkspaceRole, WorkspaceRoleType


class WorkspaceManager(models.Manager):
    """
    Manager for Workspace model.
    """

    def create(self, name, created_by, description=""):
        """
        Create a new workspace.
        """
        with transaction.atomic():
            workspace = self.model(name=name, description=description)
            workspace.save()

            workspace_member = WorkspaceRole.objects.create(
                user=created_by,
                workspace=workspace,
                role_type=WorkspaceRoleType.OWNER,
            )

            return workspace, workspace_member

    def add_user(self, workspace, user, role_type):
        """
        Add a user to a workspace with a role.
        """

        return WorkspaceRole.objects.create(user=user, workspace=workspace, role_type=role_type)

    def get_user_workspaces(self, user):
        """
        Get all workspaces for a user.
        """
        workspace_roles = WorkspaceRole.objects.filter(user=user)
        workspace_ids = workspace_roles.values_list("workspace_id", flat=True)
        return self.model.objects.filter(id__in=workspace_ids)

    def get_workspace_users(self, workspace):
        """
        Get all users for a workspace.
        """

        return WorkspaceRole.objects.filter(workspace=workspace)


class Workspace(models.Model):
    """
    Workspace model representing a group or organization.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique ID",
    )
    name = models.CharField(max_length=255, help_text="Workspace name")
    description = models.TextField(blank=True, null=True, help_text="Optional description")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation timestamp")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    # Manager
    objects = WorkspaceManager()

    class Meta:
        """Meta class for the Workspace model."""

        db_table = "workspaces"
        verbose_name = "Workspace"
        verbose_name_plural = "Workspaces"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"
