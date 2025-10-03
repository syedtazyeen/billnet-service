"""
Agent models for conversations and messages
"""

import uuid
from django.db import models
from apps.users.models import User
from apps.workspaces.models.workspace import Workspace


class Conversation(models.Model):
    """
    Represents a conversation thread between a user and agents
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique conversation ID",
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="conversations",
        help_text="Workspace this conversation belongs to",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conversations",
        help_text="User who owns this conversation",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Conversation title (auto-generated from first message)",
    )
    agent_type = models.CharField(
        max_length=50,
        default="general",
        help_text="Type of agent handling this conversation (general, support, invoice)",
    )
    llm_provider = models.CharField(
        max_length=50,
        default="gemini",
        help_text="LLM provider used for this conversation",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for the conversation",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this conversation is active",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp",
    )

    class Meta:
        """Meta class for the Conversation model"""

        db_table = "agent_conversations"
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["workspace", "user", "-updated_at"]),
            models.Index(fields=["workspace", "-updated_at"]),
            models.Index(fields=["user", "-updated_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title or 'Conversation'}"

    objects = models.Manager()


class Message(models.Model):
    """
    Represents a single message in a conversation
    """

    ROLE_USER = "user"
    ROLE_AGENT = "agent"
    ROLE_SYSTEM = "system"

    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_AGENT, "Agent"),
        (ROLE_SYSTEM, "System"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique message ID",
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="Conversation this message belongs to",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="User who sent this message",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text="Role of the message sender",
    )
    content = models.TextField(
        help_text="Message content",
    )
    agent_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Type of agent that generated this message (if role=agent)",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata (context, tokens used, etc.)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp",
    )

    objects = models.Manager()

    class Meta:
        """Meta class for the Message model"""

        db_table = "agent_messages"
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.role}: {self.content}"
