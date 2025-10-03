"""
Pluggable intent routing
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from enum import Enum


class BaseIntentRouter(ABC):
    """Abstract base class for intent detection"""

    @abstractmethod
    def detect_intent(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, float]:
        """
        Detect intent from a query and optional context.

        Returns:
            A tuple of (intent_name, confidence_score).
        """
        pass


class AgentIntent(Enum):
    """Agent intents with descriptions"""

    GENERAL = ("general", "General conversation and support")
    INVOICE = ("invoice", "Invoice management and processing")

    def __init__(self, intent_name: str, description: str):
        self.intent_name = intent_name
        self.description = description


class LLMIntentRouter(BaseIntentRouter):
    """Simple LLM-like intent detection using keyword matching with confidence scores"""

    def __init__(self, intent_descriptions: Optional[Dict[str, str]] = None):
        """
        Parameters:
            intent_descriptions: dict mapping intent_name -> description for matching
        """
        self.intent_descriptions = intent_descriptions or {}

        # Pre-compute keywords per intent for efficient matching
        self.intent_keywords = {
            intent_name: set(desc.lower().split())
            for intent_name, desc in self.intent_descriptions.items()
        }

    def detect_intent(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Tuple[AgentIntent, float]:
        """
        Detect the best matching intent for the query.

        Returns:
            A tuple of (AgentIntent enum member, confidence score between 0 and 1).
        """
        query_words = set(query.lower().split())
        best_intent = AgentIntent.GENERAL
        best_score = 0.0

        for intent in AgentIntent:
            # Gracefully handle missing keywords in intent_keywords
            keywords = self.intent_keywords.get(intent.intent_name, set())
            if not keywords:
                continue
            intersection = query_words.intersection(keywords)
            score = len(intersection) / len(keywords)

            if score > best_score:
                best_intent = intent
                best_score = score

        # Threshold fallback
        if best_score < 0.5:
            best_intent = AgentIntent.GENERAL
            best_score = 0.0

        return best_intent, best_score

    def register_intent(self, intent_name: str, description: str):
        """
        Register or update intent description and keywords.
        """
        self.intent_descriptions[intent_name] = description
        self.intent_keywords[intent_name] = set(description.lower().split())
