"""Utility helpers for the Wedding Management Dashboard."""
from typing import Any


def get_lang_value(json_field: Any, language: str, fallback: str = "en") -> str:
    """Extract a localized value from a JSON multilingual field.

    Args:
        json_field: A dict like {"en": "Hello", "km": "សួស្តី"} or None.
        language: The desired language key ("en" or "km").
        fallback: Fallback language if the desired key is missing.

    Returns:
        The localized string, or empty string if nothing is found.
    """
    if not json_field or not isinstance(json_field, dict):
        return ""
    return json_field.get(language) or json_field.get(fallback) or ""
