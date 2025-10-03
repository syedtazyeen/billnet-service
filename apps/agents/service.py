"""
Agent Service for handling conversation and message operations
"""

import json
import logging
from typing import Dict, Any, Optional, Generator
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import StreamingHttpResponse
from rest_framework import status

from apps.agents.models import Conversation, Message
from apps.agents.figents.v1.conversation import ConversationAgent
from apps.agents.figents.v1.invoice import InvoiceAgent
from apps.agents.intents import LLMIntentRouter, AgentIntent

User = get_user_model()
logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations and messages with integrated agent handling."""

    def __init__(self):
        self.intent_router = LLMIntentRouter(
            {
                AgentIntent.GENERAL.intent_name: AgentIntent.GENERAL.description,
                AgentIntent.INVOICE.intent_name: AgentIntent.INVOICE.description,
            }
        )

    def create_message(
        self,
        workspace_id: str,
        user: User,
        message_content: str,
        conversation_id: Optional[str] = None,
        agent_type: str = "general",
        llm_provider: str = "gemini",
        stream: bool = False,
    ) -> Message:
        """
        Create a user message, optionally a new conversation, and either return the message (streaming)
        or synchronously obtain the agent's response message.

        Args:
            workspace_id: Workspace identifier.
            user: Message author user.
            message_content: Text content from user.
            conversation_id: Existing conversation to attach message to, if any.
            agent_type: Type of agent to handle conversation.
            llm_provider: LLM provider identifier.
            stream: If True, return user message immediately; else wait for agent response synchronously.

        Returns:
            Message instance of either the user message (stream=True) or agent's response message (stream=False).
        """
        try:
            with transaction.atomic():
                conversation = self._get_or_create_conversation(
                    workspace_id, user, conversation_id, agent_type, llm_provider, message_content
                )

                user_message = Message.objects.create(
                    conversation=conversation,
                    user=user,
                    role=Message.ROLE_USER,
                    content=message_content,
                    agent_type=conversation.agent_type,
                )

                if stream:
                    conversation.save()
                    logger.info(
                        "Created user message %s for user %s (stream mode).",
                        user_message.id,
                        user.id,
                    )
                    return user_message

                # Synchronous agent response
                conversation_agent = self.get_conversation_agent(
                    conversation.workspace_id, conversation.llm_provider
                )
                conversation_context = self.get_conversation_context(conversation)

                agent_response = conversation_agent.route_query(
                    user_message.content, conversation_context
                )

                intent_value = agent_response.get("intent")
                if hasattr(intent_value, "intent_name"):
                    intent_value = intent_value.intent_name

                workspace_id_str = (
                    str(agent_response.get("workspace_id", ""))
                    if agent_response.get("workspace_id")
                    else ""
                )

                agent_message = Message.objects.create(
                    conversation=conversation,
                    user=user,
                    role=Message.ROLE_AGENT,
                    content=agent_response.get(
                        "response", "I'm sorry, I couldn't process that request."
                    ),
                    agent_type=intent_value or conversation.agent_type,
                    metadata={
                        "intent": intent_value,
                        "confidence": agent_response.get("confidence"),
                        "query": agent_response.get("query"),
                        "workspace_id": workspace_id_str,
                    },
                )

                conversation.save()
                logger.info(
                    "Created user message %s and agent response %s for user %s.",
                    user_message.id,
                    agent_message.id,
                    user.id,
                )
                return agent_message

        except ObjectDoesNotExist:
            logger.error("Conversation %s not found for user %s.", conversation_id, user.id)
            raise
        except Exception as exc:
            logger.error("Error creating message: %s", exc, exc_info=True)
            raise

    def _get_or_create_conversation(
        self,
        workspace_id: str,
        user: User,
        conversation_id: Optional[str],
        agent_type: str,
        llm_provider: str,
        first_message: str,
    ) -> Conversation:
        """Retrieve existing or create a new conversation, with a clean title if new."""
        if conversation_id:
            conversation = Conversation.objects.get(
                id=conversation_id, user=user, workspace_id=workspace_id, is_active=True
            )
        else:
            conversation = Conversation.objects.create(
                workspace_id=workspace_id,
                user=user,
                agent_type=agent_type,
                llm_provider=llm_provider,
                is_active=True,
                title=self._generate_conversation_title(first_message),
            )
        return conversation

    def get_conversation_agent(
        self, workspace_id: str, llm_provider: str = "gemini"
    ) -> ConversationAgent:
        """Initialize and return a configured ConversationAgent instance."""
        try:
            invoice_agent = InvoiceAgent(workspace_id, llm_provider)
            conversation_agent = ConversationAgent(
                workspace_id=workspace_id,
                intent_router=self.intent_router,
                llm_provider=llm_provider,
                invoice_agent=invoice_agent,
            )
            return conversation_agent
        except Exception as exc:
            logger.error("Error initializing conversation agent: %s", exc, exc_info=True)
            raise

    def get_conversation_context(self, conversation: Conversation) -> Dict[str, Any]:
        """Build a context dictionary including recent messages and metadata for the conversation."""
        try:
            recent_messages = conversation.messages.order_by("-created_at")[:10]
            return {
                "conversation_id": str(conversation.id),
                "workspace_id": str(conversation.workspace_id),
                "agent_type": conversation.agent_type,
                "llm_provider": conversation.llm_provider,
                "recent_messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "created_at": msg.created_at.isoformat(),
                        "agent_type": msg.agent_type,
                    }
                    for msg in recent_messages
                ],
                "conversation_metadata": conversation.metadata or {},
            }
        except Exception as exc:
            logger.error("Error building conversation context: %s", exc, exc_info=True)
            return {}

    def _generate_conversation_title(self, first_message: str) -> str:
        """Generate a concise, single-line title from the first message content."""
        try:
            title = " ".join(first_message.strip().split())[:50]
            if len(first_message) > 50:
                title += "..."
            return title or "New Conversation"
        except Exception as exc:
            logger.error("Error generating conversation title: %s", exc, exc_info=True)
            return "New Conversation"

    def get_streaming_agent_response(
        self,
        user_message: Message,
        conversation_agent: ConversationAgent,
        conversation_context: Dict[str, Any],
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream the agent response chunks from conversation agent.

        On final chunk, create and save the agent response message.

        Yields:
            Dict chunks for streaming.
        """
        try:
            full_response = ""
            intent_value = None
            confidence = None
            workspace_id = None

            for chunk in conversation_agent.route_query_streaming(
                user_query=user_message.content,
                user_context=conversation_context,
            ):
                if intent_value is None:
                    intent_value = chunk.get("intent")
                    confidence = chunk.get("confidence")
                    workspace_id = chunk.get("workspace_id")

                content_chunk = chunk.get("content")
                if content_chunk:
                    full_response += content_chunk

                yield chunk

                if chunk.get("done", False):
                    try:
                        if hasattr(intent_value, "intent_name"):
                            intent_value = intent_value.intent_name

                        if workspace_id is not None:
                            workspace_id = str(workspace_id)

                        agent_message = Message.objects.create(
                            conversation=user_message.conversation,
                            user=user_message.user,
                            role=Message.ROLE_AGENT,
                            content=full_response or "I'm sorry, I couldn't process that request.",
                            agent_type=intent_value or user_message.conversation.agent_type,
                            metadata={
                                "intent": intent_value,
                                "confidence": confidence,
                                "query": user_message.content,
                                "workspace_id": workspace_id,
                            },
                        )

                        user_message.conversation.save()
                        logger.info(
                            "Created streaming agent response message %s for user %s.",
                            agent_message.id,
                            user_message.user.id,
                        )

                        # Yield final chunk with message id metadata
                        yield {
                            "content": "",
                            "done": True,
                            "message_id": str(agent_message.id),
                            "intent": intent_value,
                            "confidence": confidence,
                            "workspace_id": workspace_id,
                        }

                    except Exception as exc:
                        logger.error(
                            "Error creating agent message during streaming: %s", exc, exc_info=True
                        )
                        yield {
                            "content": "",
                            "done": True,
                            "error": f"Failed to save agent response: {exc}",
                        }
        except Exception as exc:
            logger.error("Error in streaming response generator: %s", exc, exc_info=True)
            yield {
                "content": "I'm sorry, I encountered an error processing your request.",
                "done": True,
                "error": str(exc),
            }

    def create_streaming_response(
        self,
        user_message,
        conversation_agent,
        conversation_context,
        initial_data_type="conversation",
        initial_serializer_class=None,
    ):
        """
        Create a streaming response for agent conversations.

        Args:
            user_message: The user message object
            conversation_agent: The conversation agent instance
            conversation_context: The conversation context
            initial_data_type: Type of initial data to stream ("conversation" or "message")
            initial_serializer_class: Serializer class for initial data

        Returns:
            StreamingHttpResponse: The streaming response
        """
        from apps.core.utils.json import safe_chunk_for_json

        def stream_response():
            # Yield initial data first
            if initial_data_type == "conversation":
                serializer = initial_serializer_class(user_message.conversation)
            else:  # message
                serializer = initial_serializer_class(user_message, include_user=True)

            data = safe_chunk_for_json(serializer.data)
            yield f"data: {json.dumps({'type': initial_data_type, 'data': data})}\n\n"

            # Stream agent response chunks with safe serialization
            for chunk in self.get_streaming_agent_response(
                user_message, conversation_agent, conversation_context
            ):
                chunk_type = "complete" if chunk.get("done", False) else "chunk"
                safe_chunk = safe_chunk_for_json(chunk)
                yield f"data: {json.dumps({'type': chunk_type, 'data': safe_chunk})}\n\n"

        return StreamingHttpResponse(
            stream_response(),
            content_type="text/event-stream",
            status=status.HTTP_201_CREATED,
        )


# Global singleton service instance
conversation_service = ConversationService()
