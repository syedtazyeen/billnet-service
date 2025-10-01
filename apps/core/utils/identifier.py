"""
Identifier validation and type identification utilities.
"""

import re

_EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
_PHONE_PATTERN = re.compile(r"^\+?\d{7,15}$")


def is_valid_identifier(value: str) -> bool:
    """
    Validate the identifier.
    """
    if not isinstance(value, str) or not value.strip():
        return False

    value = value.strip()
    if _EMAIL_PATTERN.match(value) or _PHONE_PATTERN.match(value):
        return True
    return False

def get_identifier_type(value: str) -> str | None:
    """
    Get the type of the identifier.
    """
    value = value.strip()
    if _EMAIL_PATTERN.match(value):
        return "email"
    if _PHONE_PATTERN.match(value):
        return "phone"
    return None
