"""
Workspace role models
"""

import uuid
from django.db import models
from apps.users.models import User


class WorkspaceRoleType(models.TextChoices):
    """
    Workspace role types.
    """

    OWNER = "owner", "Owner"
    MEMBER = "member", "Member"


class WorkspaceRoleManager(models.Manager):
    """
    Custom manager for WorkspaceRole model.
    """

    def create(self, user: User, workspace, role_type):
        """Create a new workspace role."""
        if self.model.objects.filter(user=user, workspace=workspace).exists():
            raise ValueError("User already has a role in the workspace")
        return super().create(user=user, workspace=workspace, type=role_type)

    def update_role(self, role, role_type):
        """Update a workspace role."""
        if not self.model.objects.filter(id=role.id).exists():
            raise ValueError("Workspace role not found")
        role.type = role_type
        role.save()
        return role

    def delete(self, role):
        """Delete a workspace role."""
        role.delete()

    def get_by_user_and_workspace(self, user: User, workspace):
        """Get a workspace role by user and workspace."""
        return super().model.objects.get(user=user, workspace=workspace)

    def get_by_user(self, user: User):
        """Get all workspace roles by user."""
        return super().model.objects.filter(user=user)

    def get_by_workspace(self, workspace):
        """Get all workspace roles by workspace."""
        return super().model.objects.filter(workspace=workspace)


class WorkspaceRole(models.Model):
    """
    Workspace role linking users to workspaces with roles.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique role ID",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workspace_roles",
        help_text="User",
    )
    workspace = models.ForeignKey(
        "Workspace",
        on_delete=models.CASCADE,
        related_name="roles",
        help_text="Workspace",
    )
    type = models.CharField(
        max_length=20,
        choices=WorkspaceRoleType.choices,
        default=WorkspaceRoleType.MEMBER,
        help_text="Type of the role",
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation timestamp")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    # Manager
    objects = WorkspaceRoleManager()

    class Meta:
        """Meta class for the WorkspaceRole model."""

        db_table = "workspace_roles"
        verbose_name = "Workspace Role"
        verbose_name_plural = "Workspace Roles"
        unique_together = ("user", "workspace")
        ordering = ["type", "updated_at"]

    def __str__(self) -> str:
        return f"{self.user} - {self.workspace} ({self.type})"
