"""
JSON utilities for safe serialization
"""

import uuid
from datetime import datetime, date, time
from decimal import Decimal


def safe_chunk_for_json(chunk: dict) -> dict:
    """
    Convert any non-serializable objects in chunk to JSON-friendly formats.
    Handles AgentIntent instances, UUIDs, and other common non-serializable types.
    """
    from apps.agents.intents import AgentIntent  # pylint: disable=import-outside-toplevel

    # Type converter mapping for cleaner code
    type_converters = {
        AgentIntent: lambda x: x.intent_name,
        uuid.UUID: str,
        datetime: lambda x: x.isoformat(),
        date: lambda x: x.isoformat(),
        time: lambda x: x.isoformat(),
        Decimal: float,
    }

    def convert_value(value):
        """Recursively convert non-serializable values to JSON-friendly formats"""
        # Handle collections first
        if isinstance(value, dict):
            return {k: convert_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [convert_value(item) for item in value]

        # Handle specific types using the converter mapping
        for type_class, converter in type_converters.items():
            if isinstance(value, type_class):
                return converter(value)

        # Return as-is for JSON-serializable types
        return value

    return {k: convert_value(v) for k, v in chunk.items()}
