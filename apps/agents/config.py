"""
LLM Configuration for CrewAI agents
"""

from typing import Dict, Any
from decouple import config

try:
    import google.generativeai as genai
except ImportError:
    genai = None


DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


class LLMConfig:
    """LLM Configuration manager for multi-model support."""

    def __init__(self):
        self.gemini_api_key = config("GEMINI_API_KEY", default="")
        self._setup_gemini()

    def _setup_gemini(self):
        """Initialize Gemini configuration if API key and library are available."""
        if self.gemini_api_key and genai:
            genai.configure(api_key=self.gemini_api_key)

    def get_gemini_model(self, model_name: str = DEFAULT_GEMINI_MODEL) -> Any:
        """Return a Gemini model instance by valid model name."""
        if not self.gemini_api_key:
            raise ValueError("Gemini API key not configured.")

        if not genai:
            raise ValueError("Google Generative AI library is not installed.")

        # Mapping for model API names
        model_mapping = {
            "gemini-2.0-flash": "gemini-2.0-flash",
        }
        actual_model_name = model_mapping.get(model_name, DEFAULT_GEMINI_MODEL)
        return genai.GenerativeModel(actual_model_name)

    def get_llm_config(
        self, provider: str = "gemini", model_name: str = DEFAULT_GEMINI_MODEL
    ) -> Any:
        """Get LLM configuration for CrewAI based on provider."""
        if provider == "gemini":
            # Return the Gemini model instance directly
            return self.get_gemini_model(model_name)
        raise ValueError(f"Unsupported LLM provider: {provider}")

    def get_available_models(self) -> Dict[str, list]:
        """Return a dictionary of available models for each provider."""
        return {
            "gemini": [
                DEFAULT_GEMINI_MODEL,
            ]
        }


# Global LLM config instance
llm_config = LLMConfig()
