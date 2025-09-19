"""
String value type for Sass.
"""

from typing import Optional
from .base import Value


class SassString(Value):
    """A Sass string value."""
    
    def __init__(self, text: str, quoted: bool = True):
        self._text = text
        self._quoted = quoted
    
    @property
    def text(self) -> str:
        """The string content (matches Node.js text property)."""
        return self._text
    
    @property
    def has_quotes(self) -> bool:
        """Whether this string has quotes (matches Node.js hasQuotes property)."""
        return self._quoted
    
    @property
    def sass_length(self) -> int:
        """The length of this string in Sass (matches Node.js sassLength property)."""
        # In Sass, string length is based on Unicode code points
        return len(self._text)
    
    @staticmethod
    def empty(quoted: bool = True) -> 'SassString':
        """
        Create an empty string (matches Node.js SassString.empty() method).
        
        Args:
            quoted: Whether the empty string should be quoted
            
        Returns:
            An empty SassString
        """
        return SassString("", quoted=quoted)
    
    @property
    def is_truthy(self) -> bool:
        """Strings are always truthy in Sass."""
        return True
    
    @property
    def separator(self) -> Optional[str]:
        """Strings don't have separators."""
        return None
    
    @property
    def has_brackets(self) -> bool:
        """Strings don't have brackets."""
        return False
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, SassString):
            return False
        return self._text == other._text and self._quoted == other._quoted
    
    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash((self._text, self._quoted))
    
    def __str__(self) -> str:
        """String representation matching Sass output."""
        if self._quoted:
            # Escape quotes in the content
            escaped = self._text.replace('"', '\\"')
            return f'"{escaped}"'
        return self._text
    
    def __repr__(self) -> str:
        """Python representation."""
        return f"SassString({self._text!r}, quoted={self._quoted})"
