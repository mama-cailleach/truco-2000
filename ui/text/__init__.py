"""
TextManager for localization (i18n) in Truco 2000.

Loads language-specific string dictionaries and provides access methods.
"""

from importlib import import_module
from typing import Dict, Any


class TextManager:
    """
    Manages localized UI strings.
    
    Use get_text(key, **params) to retrieve strings by key.
    """

    def __init__(self, locale: str = "pt_br") -> None:
        self.locale = locale
        self.strings: Dict[str, str] = {}
        self.load_locale(locale)

    def load_locale(self, locale: str) -> None:
        """Load a locale module and store its STRINGS dictionary."""
        try:
            module = import_module(f"ui.text.locales.{locale}")
            data = getattr(module, "STRINGS", {})
            if not isinstance(data, dict):
                raise ValueError("Locale file must define STRINGS dict")
            self.strings = data
            self.locale = locale
        except Exception as e:
            raise RuntimeError(f"Failed to load locale '{locale}': {e}")

    def get_text(self, key: str, **params: Any) -> str:
        """Get a localized string by key, optionally formatting with params."""
        value = self.strings.get(key)
        if value is None:
            # Return the key to make missing strings visible during dev
            return key
        if params:
            try:
                return value.format(**params)
            except Exception:
                # Fallback to raw value if formatting fails
                return value
        return value

    def set_locale(self, locale: str) -> None:
        """Switch to a different locale at runtime."""
        self.load_locale(locale)
