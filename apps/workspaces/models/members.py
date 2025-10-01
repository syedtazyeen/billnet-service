"""
Workspace member models
"""

import uuid
from django.db import models
from apps.users.models import User


class WorkspaceMemberRole(models.TextChoices):
    """
    Workspace member role choices.
    """

    OWNER = "owner", "Owner"
    MEMBER = "member", "Member"


class WorkspaceMemberManager(models.Manager):
    """
    Custom manager for WorkspaceMember model.
    """

    def create(self, user: User, workspace, role):
        """Create a new workspace member."""
        if self.model.objects.filter(user=user, workspace=workspace).exists():
            raise ValueError("User already in the workspace")
        return super().create(user=user, workspace=workspace, role=role)

    def update_role(self, member, role):
        """Update a workspace member."""
        if not self.model.objects.filter(id=member.id).exists():
            raise ValueError("Workspace member not found")
        member.role = role
        member.save()
        return member

    def delete(self, member):
        """Delete a workspace member."""
        member.delete()

    def get_by_user_and_workspace(self, user: User, workspace):
        """Get a workspace member by user and workspace."""
        return super().model.objects.get(user=user, workspace=workspace)

    def get_by_user(self, user: User):
        """Get all workspace members by user."""
        return super().model.objects.filter(user=user)

    def get_by_workspace(self, workspace):
        """Get all workspace members by workspace."""
        return super().model.objects.filter(workspace=workspace)


class WorkspaceMember(models.Model):
    """
    Workspace member linking users to workspaces with roles.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique member ID",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workspace_members",
        help_text="User",
    )
    workspace = models.ForeignKey(
        "Workspace",
        on_delete=models.CASCADE,
        related_name="members",
        help_text="Workspace",
    )
    role = models.CharField(
        max_length=20,
        choices=WorkspaceMemberRole.choices,
        default=WorkspaceMemberRole.MEMBER,
        help_text="Role of the user",
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation timestamp")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    # Manager
    objects = WorkspaceMemberManager()

    class Meta:
        """Meta class for the WorkspaceMember model."""

        db_table = "workspace_members"
        verbose_name = "Workspace Member"
        verbose_name_plural = "Workspace Members"
        unique_together = ("user", "workspace")
        ordering = ["role", "updated_at"]

    def __str__(self) -> str:
        return f"{self.user} - {self.workspace} ({self.role})"
