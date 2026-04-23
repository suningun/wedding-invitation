"""Utility helpers for the Wedding Management Dashboard."""

from typing import Any


# Extract localized text from JSON multilingual fields with fallback
def get_lang_value(json_field: Any, language: str, fallback: str = "en") -> str:
    """Extract localized value from JSON field {"en": "...", "km": "..."} with fallback.

    This utility handles multilingual content stored as JSON:
    - Fetches requested language key first
    - Falls back to default language if not found
    - Returns empty string if field is empty/invalid
    """
    if not json_field or not isinstance(json_field, dict):
        return ""
    return json_field.get(language) or json_field.get(fallback) or ""
