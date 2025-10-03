"""
CrewAI-based Base Agent for workspace agents
"""

from typing import Optional, Dict, Any, Generator, List
import logging

try:
    from crewai import Agent, Task
    from apps.agents.config import llm_config
except ImportError:
    Agent = None
    Task = None
    llm_config = None


logger = logging.getLogger(__name__)


class BaseAgentContext:
    """Base class to hold and update agent context."""

    def __init__(
        self,
        workspace_id: str,
        agent_name: str,
        llm_provider: str = "gemini",
        initial_context: Optional[Dict[str, Any]] = None,
    ):
        self.workspace_id = workspace_id
        self.agent_name = agent_name
        self.llm_provider = llm_provider
        self.context: Dict[str, Any] = initial_context.copy() if initial_context else {}

    def update(self, new_context: Dict[str, Any]) -> "BaseAgentContext":
        """Update the current context with new data."""
        self.context.update(new_context)
        return self


class BaseWorkspaceAgent:
    """
    Base class for CrewAI workspace agents with direct LLM integration.

    Subclasses must implement 'role', 'goal', 'backstory', and 'tools' properties.
    """

    def __init__(self, workspace_id: str, agent_name: str, llm_provider: str = "gemini"):
        self.workspace_id = workspace_id
        self.agent_name = agent_name
        self.llm_provider = llm_provider
        self.llm_config = llm_config.get_llm_config(llm_provider) if llm_config else {}
        self._agent: Optional[Agent] = None

    @property
    def role(self) -> str:
        raise NotImplementedError("Subclasses must define agent role")

    @property
    def goal(self) -> str:
        raise NotImplementedError("Subclasses must define agent goal")

    @property
    def backstory(self) -> str:
        raise NotImplementedError("Subclasses must define agent backstory")

    @property
    def tools(self) -> List[Any]:
        raise NotImplementedError("Subclasses must define agent tools")

    def get_agent(self) -> Agent:
        """Get or create a CrewAI agent instance without built-in LLM."""
        if Agent is None:
            raise RuntimeError("CrewAI Agent is not available (missing dependencies)")

        if self._agent is None:
            try:
                self._agent = Agent(
                    role=self.role,
                    goal=self.goal,
                    backstory=self.backstory,
                    tools=self.tools,
                    verbose=True,
                    allow_delegation=False,
                )
                logger.debug("CrewAI Agent created successfully.")
            except Exception as exc:
                logger.error("CrewAI agent creation failed: %s", exc)
                raise
        return self._agent

    def create_task(self, description: str, expected_output: str) -> Task:
        """Create a CrewAI task to be executed by the agent."""
        if Task is None:
            raise RuntimeError("CrewAI Task is not available (missing dependencies)")

        try:
            return Task(
                description=description, expected_output=expected_output, agent=self.get_agent()
            )
        except Exception as exc:
            logger.error("Failed to create task: %s", exc)
            raise

    def execute_task(self, task_description: str, expected_output: str) -> str:
        """Execute a single task synchronously using direct LLM call."""
        return self._execute_with_direct_llm(task_description, expected_output)

    def _build_prompt(self, task_description: str, expected_output: str) -> str:
        """Build the prompt string to send to the LLM."""
        return (
            f"Role: {self.role}\n"
            f"Goal: {self.goal}\n"
            f"Backstory: {self.backstory}\n\n"
            f"Task: {task_description}\n\n"
            f"Expected Output: {expected_output}\n\n"
            "Please provide a response that fulfills this task:\n"
        )

    def _execute_with_direct_llm(self, task_description: str, expected_output: str) -> str:
        """Use direct LLM call to execute tasks synchronously, bypassing CrewAI internals."""
        try:
            from apps.agents.config import llm_config as config

            prompt = self._build_prompt(task_description, expected_output)
            model = config.get_gemini_model()
            response = model.generate_content(prompt)

            text = response.text if response and response.text else None
            if text:
                logger.debug("LLM generated a successful response.")
                return text

            logger.warning("LLM returned empty text.")
            return "I apologize, but I couldn't generate a response for this task."

        except Exception as exc:
            logger.error("Direct LLM call failed: %s", exc)
            return "I apologize, but I'm unable to process your request at the moment. Please try again later."

    def execute_task_streaming(
        self, task_description: str, expected_output: str
    ) -> Generator[Dict[str, Any], None, None]:
        """Execute a single task with streaming response using direct LLM call."""
        return self._execute_with_direct_llm_streaming(task_description, expected_output)

    def _execute_with_direct_llm_streaming(
        self, task_description: str, expected_output: str
    ) -> Generator[Dict[str, Any], None, None]:
        """Use direct LLM call to execute tasks with streaming, bypassing CrewAI internals."""
        try:
            from apps.agents.config import llm_config as config

            prompt = self._build_prompt(task_description, expected_output)
            model = config.get_gemini_model()
            response_stream = model.generate_content(prompt, stream=True)

            full_response = ""

            for chunk in response_stream:
                chunk_text = getattr(chunk, "text", None)
                if chunk_text:
                    full_response += chunk_text
                    yield {"content": chunk_text, "done": False}

            yield {"content": "", "done": True, "full_response": full_response}

        except Exception as exc:
            logger.error("Direct LLM streaming call failed: %s", exc)
            yield {
                "content": "I apologize, but I'm unable to process your request at the moment. Please try again later.",
                "done": True,
                "error": str(exc),
            }

    def execute_multiple_tasks(self, tasks: List[tuple[str, str]]) -> List[str]:
        """Execute multiple tasks synchronously using direct LLM calls."""
        results = []
        for description, output in tasks:
            try:
                result = self._execute_with_direct_llm(description, output)
                results.append(result)
            except Exception as exc:
                logger.error("Failed to execute task: %s", exc)
                results.append("")
        return results

    def get_workspace_context(self) -> BaseAgentContext:
        """Return current workspace context wrapper."""
        return BaseAgentContext(
            workspace_id=self.workspace_id,
            agent_name=self.agent_name,
            llm_provider=self.llm_provider,
        )
