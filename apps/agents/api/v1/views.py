"""
API views for agents
"""

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from apps.workspaces.permissions import IsWorkspaceMember
from apps.workspaces.models.workspace import Workspace
from apps.agents.api.v1.serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer,
)
from apps.agents.models import Conversation
from apps.agents.service import conversation_service


@extend_schema(tags=["Agent Conversations"])
@permission_classes([IsAuthenticated])
class ConversationView(GenericAPIView):
    """
    GET: List conversations with last message for the requesting user
    POST: Create a new conversation and trigger agent response
    """

    @extend_schema(
        summary="List all conversations",
        description="Retrieve all conversations for the authenticated user in the workspace",
        responses={200: ConversationSerializer(many=True)},
    )
    @permission_classes([IsWorkspaceMember])
    def get(self, request, **kwargs):
        """
        List all conversations for the authenticated user in the workspace
        """
        workspace_id = kwargs.get("workspace_id")
        workspace = get_object_or_404(Workspace, id=workspace_id)

        queryset = (
            Conversation.objects.filter(workspace=workspace, user=request.user)
            .prefetch_related("messages")
            .order_by("-updated_at")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ConversationSerializer(page, many=True, include_user=True)
            return self.get_paginated_response(serializer.data)

        serializer = ConversationSerializer(queryset, many=True, include_user=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create a new conversation",
        description="Create a new conversation in the workspace with an initial message",
        request=ConversationCreateSerializer,
        responses={201: ConversationSerializer},
    )
    @permission_classes([IsWorkspaceMember])
    def post(self, request, **kwargs):
        """
        Create a new conversation and trigger agent response
        """
        workspace_id = kwargs.get("workspace_id")
        get_object_or_404(Workspace, id=workspace_id)

        serializer = ConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stream = serializer.validated_data.get("stream", False)

        try:
            user_message = conversation_service.create_message(
                workspace_id=workspace_id,
                user=request.user,
                message_content=serializer.validated_data["message"],
                stream=stream,
            )

            if stream:
                conversation_agent = conversation_service.get_conversation_agent(
                    workspace_id=user_message.conversation.workspace_id,
                    llm_provider=user_message.conversation.llm_provider,
                )
                conversation_context = conversation_service.get_conversation_context(
                    user_message.conversation
                )

                return conversation_service.create_streaming_response(
                    user_message=user_message,
                    conversation_agent=conversation_agent,
                    conversation_context=conversation_context,
                    initial_data_type="conversation",
                    initial_serializer_class=ConversationSerializer,
                )

            # Non-streaming: return full conversation data with agent response
            conv_serializer = ConversationSerializer(user_message.conversation)
            return Response(conv_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as exc:
            return Response(
                {"error": f"Failed to create conversation: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=["Agent Conversations"])
@permission_classes([IsAuthenticated])
class ConversationDetailView(GenericAPIView):
    """
    GET: Retrieve conversation by ID (ensuring ownership and workspace membership)
    """

    @extend_schema(
        summary="Retrieve a conversation by ID",
        description="Retrieve conversation with ownership and workspace membership validation",
        responses={200: ConversationSerializer},
    )
    @permission_classes([IsWorkspaceMember])
    def get(self, request, conversation_id, **kwargs):
        """
        Retrieve a conversation by ID
        """
        workspace_id = kwargs.get("workspace_id")
        workspace = get_object_or_404(Workspace, id=workspace_id)

        conversation = get_object_or_404(
            Conversation, pk=conversation_id, user=request.user, workspace=workspace
        )
        serializer = ConversationSerializer(conversation, include_user=True)
        return Response(serializer.data)


@extend_schema(tags=["Agent Conversations"])
@permission_classes([IsAuthenticated])
class MessageView(GenericAPIView):
    """
    GET: List all messages for a conversation
    POST: Create a message in a conversation and trigger agent response
    """

    @extend_schema(
        summary="List all messages for a conversation",
        description="Retrieve all messages for a conversation owned by the user in the workspace",
        responses={200: MessageSerializer(many=True)},
    )
    @permission_classes([IsWorkspaceMember])
    def get(self, request, conversation_id, **kwargs):
        """
        List all messages for a conversation
        """
        workspace_id = kwargs.get("workspace_id")
        workspace = get_object_or_404(Workspace, id=workspace_id)

        conversation = get_object_or_404(
            Conversation, pk=conversation_id, user=request.user, workspace=workspace
        )
        messages = conversation.messages.order_by("created_at")

        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True, include_user=True)
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True, include_user=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create a message in a conversation",
        description="Create a message for a conversation owned by the user and obtain agent response",
        request=MessageCreateSerializer,
        responses={201: MessageSerializer},
    )
    @permission_classes([IsWorkspaceMember])
    def post(self, request, conversation_id, **kwargs):
        """
        Create a message in a conversation and trigger agent response
        """
        workspace_id = kwargs.get("workspace_id")
        get_object_or_404(Workspace, id=workspace_id)

        # Verify conversation ownership/access
        get_object_or_404(
            Conversation, pk=conversation_id, user=request.user, workspace_id=workspace_id
        )

        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stream = serializer.validated_data.get("stream", False)

        try:
            user_message = conversation_service.create_message(
                workspace_id=workspace_id,
                user=request.user,
                message_content=serializer.validated_data["content"],
                conversation_id=conversation_id,
                stream=stream,
            )

            if stream:
                conversation_agent = conversation_service.get_conversation_agent(
                    workspace_id=user_message.conversation.workspace_id,
                    llm_provider=user_message.conversation.llm_provider,
                )
                conversation_context = conversation_service.get_conversation_context(
                    user_message.conversation
                )

                return conversation_service.create_streaming_response(
                    user_message=user_message,
                    conversation_agent=conversation_agent,
                    conversation_context=conversation_context,
                    initial_data_type="message",
                    initial_serializer_class=MessageSerializer,
                )

            msg_serializer = MessageSerializer(user_message, include_user=True)
            return Response(msg_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as exc:
            return Response(
                {"error": f"Failed to add message: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
