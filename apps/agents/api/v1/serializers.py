"""
Serializers for the agents app
"""

from rest_framework import serializers
from django.db import transaction
from apps.agents.models import Message, Conversation
from apps.users.api.v1.serializers import UserSimpleSerializer


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new messages - only requires content field"""

    stream = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Whether to stream the LLM response or return it directly",
    )

    class Meta:
        """Meta class for the MessageCreateSerializer"""

        model = Message
        fields = [
            "content",
            "stream",
        ]

    def create(self, validated_data):
        """Create a new message with default values"""
        conversation = self.context.get("conversation")
        user = self.context.get("user")
        if not conversation or not user:
            raise serializers.ValidationError("Conversation and user context are required")

        if not user:
            raise serializers.ValidationError("User context is required")

        # Set default values for message creation
        validated_data["conversation"] = conversation
        validated_data["user"] = user  # Set the user who is creating the message
        validated_data["role"] = Message.ROLE_USER  # Default to user role for new messages
        validated_data["agent_type"] = conversation.agent_type  # Inherit from conversation

        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for retrieving messages - includes all fields for display"""

    user = serializers.SerializerMethodField()

    class Meta:
        """Meta class for the MessageSerializer"""

        model = Message
        fields = [
            "id",
            "role",
            "content",
            "user",
            "agent_type",
            "metadata",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user"]

    def get_user(self, obj):
        """Get user data - returns full user object if include_user is True, otherwise just ID"""
        include_user = getattr(self, "include_user", False)

        if include_user:
            return UserSimpleSerializer(obj.user).data
        return obj.user.id

    def __init__(self, *args, **kwargs):
        """Initialize serializer with include_user parameter (for compatibility)"""
        self.include_user = kwargs.pop("include_user", False)
        super().__init__(*args, **kwargs)


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new conversations - only requires message content"""

    message = serializers.CharField(
        required=True,
        help_text="Initial message content to start the conversation",
    )

    stream = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Whether to stream the LLM response or return it directly",
    )

    class Meta:
        """Meta class for the ConversationCreateSerializer"""

        model = Conversation
        fields = [
            "message",
            "stream",
        ]

    @transaction.atomic
    def create(self, validated_data):
        """Create a new conversation with an initial message atomically"""
        workspace = self.context.get("workspace")
        user = self.context.get("user")
        if not workspace or not user:
            raise serializers.ValidationError("Workspace context is required")

        # Verify user is a member of the workspace
        if not workspace.roles.filter(user=user).exists():
            raise serializers.ValidationError("You are not a member of this workspace")

        # Extract message content
        message_content = validated_data.pop("message")
        if not message_content or not message_content.strip():
            raise serializers.ValidationError("Message content cannot be empty")

        # Set default values for conversation
        conversation_data = {
            "workspace": workspace,
            "user": user,
            "agent_type": "general",  # Default agent type
            "llm_provider": "gemini",  # Default LLM provider
            "is_active": True,
        }

        try:
            # Create the conversation atomically with the initial message
            conversation = Conversation.objects.create(**conversation_data)

            # Create the initial message within the same transaction
            Message.objects.create(
                conversation=conversation,
                user=user,
                role=Message.ROLE_USER,
                content=message_content.strip(),
                agent_type=conversation.agent_type,
            )

            return conversation

        except Exception as e:
            # If any error occurs, the transaction will be rolled back automatically
            raise e


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for retrieving conversations - includes all fields for display"""

    last_message = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        """Meta class for the ConversationSerializer"""

        model = Conversation
        fields = [
            "id",
            "user",
            "title",
            "agent_type",
            "llm_provider",
            "last_message",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "last_message", "user"]

    def get_user(self, obj):
        """Get user data - returns full user object if include_user is True, otherwise just ID"""
        include_user = getattr(self, "include_user", False)

        if include_user:
            return UserSimpleSerializer(obj.user).data
        return obj.user.id

    def get_last_message(self, obj):
        """Get the last message for a conversation"""
        last = obj.messages.order_by("-created_at").first()
        if last:
            return MessageSerializer(last, include_user=self.include_user).data
        return None

    def __init__(self, *args, **kwargs):
        """Initialize serializer with include_user parameter"""
        self.include_user = kwargs.pop("include_user", False)
        super().__init__(*args, **kwargs)
