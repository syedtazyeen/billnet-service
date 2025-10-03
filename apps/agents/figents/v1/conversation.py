"""
Conversation Agent
"""

from typing import Dict, Any, Optional, Generator
from apps.agents.intents import AgentIntent

try:
    from apps.agents.figents.v1.base import BaseWorkspaceAgent
except ImportError:
    BaseWorkspaceAgent = None


class ConversationAgent(BaseWorkspaceAgent):
    """
    Conversation Agent that routes user queries via a pluggable LLMIntentRouter,
    delegating to specialized agents or handling general queries directly.
    """

    def __init__(
        self,
        workspace_id: str,
        intent_router,
        llm_provider: str = "gemini",
        support_agent: Optional[BaseWorkspaceAgent] = None,
        invoice_agent: Optional[BaseWorkspaceAgent] = None,
    ):
        super().__init__(workspace_id, "Conversation Agent", llm_provider)
        self.intent_router = intent_router
        self.support_agent = support_agent
        self.invoice_agent = invoice_agent

    @property
    def role(self) -> str:
        return f"Conversation Agent for workspace {self.workspace_id}"

    @property
    def goal(self) -> str:
        return (
            "Understand user queries and route them to the most appropriate "
            "specialized agent using intent routing, while providing conversation assistance."
        )

    @property
    def backstory(self) -> str:
        return (
            f"You are the main interface for workspace {self.workspace_id}. "
            "You use intent detection to route queries efficiently to specialized agents. "
            "You handle general questions directly if needed."
        )

    @property
    def tools(self) -> list:
        return []

    def route_query(
        self, user_query: str, user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route a user query to the appropriate specialized agent or self."""

        context = self.get_workspace_context()
        if user_context:
            context.update(user_context)

        intent_name, confidence = self.intent_router.detect_intent(user_query, context)

        if intent_name == AgentIntent.INVOICE and self.invoice_agent:
            response = self.invoice_agent.handle_invoice_query(user_query, user_context)
        else:
            response = self._handle_conversation_query(user_query, user_context)

        return {
            "intent": intent_name,
            "confidence": confidence,
            "response": response,
            "workspace_id": self.workspace_id,
            "query": user_query,
        }

    def route_query_streaming(
        self, user_query: str, user_context: Optional[Dict[str, Any]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Route a user query with streaming response from the appropriate agent."""

        context = self.get_workspace_context()
        if user_context:
            context.update(user_context)

        intent_name, confidence = self.intent_router.detect_intent(user_query, context)

        if intent_name == AgentIntent.INVOICE and self.invoice_agent:
            # Streaming not implemented for invoice agent yet
            response = self.invoice_agent.handle_invoice_query(user_query, user_context)
            yield {
                "content": response,
                "done": True,
                "intent": intent_name,
                "confidence": confidence,
                "workspace_id": self.workspace_id,
                "query": user_query,
            }
        else:
            full_response = ""
            for chunk in self._handle_conversation_query_streaming(user_query, user_context):
                full_response += chunk.get("content", "")
                chunk.update(
                    intent=intent_name,
                    confidence=confidence,
                    workspace_id=self.workspace_id,
                    query=user_query,
                )
                yield chunk

    def _handle_conversation_query(
        self, query: str, user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Handle a general conversation query synchronously."""

        context = self.get_workspace_context()
        if user_context:
            context.update(user_context)

        task_description = (
            f'Handle this conversation query for workspace {self.workspace_id}: "{query}"\n\n'
            f'Context: {getattr(context, "context", "No additional context")}\n\n'
            "Provide a helpful response that:\n"
            "- Directly addresses the query\n"
            "- Offers relevant platform information\n"
            "- Suggests next steps if appropriate\n"
            "- Routes to specific agents if the query becomes more specific\n"
        )

        expected_output = (
            "A helpful conversation response that:\n"
            "1. Addresses the user's query directly\n"
            "2. Provides relevant platform information\n"
            "3. Suggests appropriate next steps\n"
            "4. Offers to connect with specialized agents if needed\n"
            "5. Maintains a friendly, professional tone\n"
        )

        return self.execute_task(task_description, expected_output)

    def _handle_conversation_query_streaming(
        self, query: str, user_context: Optional[Dict[str, Any]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Handle a general conversation query with streaming response."""

        context = self.get_workspace_context()
        if user_context:
            context.update(user_context)

        task_description = (
            f'Handle this conversation query for workspace {self.workspace_id}: "{query}"\n\n'
            f'Context: {getattr(context, "context", "No additional context")}\n\n'
            "Provide a helpful response that:\n"
            "- Directly addresses the query\n"
            "- Offers relevant platform information\n"
            "- Suggests next steps if appropriate\n"
            "- Routes to specific agents if the query becomes more specific\n"
        )

        expected_output = (
            "A helpful conversation response that:\n"
            "1. Addresses the user's query directly\n"
            "2. Provides relevant platform information\n"
            "3. Suggests appropriate next steps\n"
            "4. Offers to connect with specialized agents if needed\n"
            "5. Maintains a friendly, professional tone\n"
        )

        yield from self.execute_task_streaming(task_description, expected_output)
