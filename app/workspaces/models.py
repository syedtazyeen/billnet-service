"""
Workspace models
"""

import uuid
from django.db import models, transaction
from app.workspaces.members.models import WorkspaceMember, WorkspaceMemberRole


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

            workspace_member = WorkspaceMember.objects.create(
                workspace=workspace,
                user=created_by,
                role=WorkspaceMemberRole.OWNER,
            )

            return workspace, workspace_member

    def add_user(self, workspace, user, role):
        """
        Add a user to a workspace with a role.
        """

        return WorkspaceMember.objects.create(workspace=workspace, user=user, role=role)

    def get_user_workspaces(self, user):
        """
        Get all workspaces for a user.
        """

        return WorkspaceMember.objects.filter(user=user)

    def get_workspace_users(self, workspace):
        """
        Get all users for a workspace.
        """

        return WorkspaceMember.objects.filter(workspace=workspace)


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
    description = models.TextField(
        blank=True, null=True, help_text="Optional description"
    )
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
