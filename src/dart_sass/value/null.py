"""
Null value type for Sass.
"""

from typing import Optional
from .base import Value


class SassNull(Value):
    """
    The Sass null value.
    
    This class cannot be directly instantiated.
    Use the provided sass_null singleton instance.
    """
    
    _construction_allowed = True
    
    def __init__(self):
        """
        Initialize a SassNull.
        
        Raises:
            TypeError: If construction is not allowed (after singleton is created)
        """
        if not SassNull._construction_allowed:
            raise TypeError(
                "SassNull() isn't allowed.\n"
                "Use sass_null instead."
            )
    
    @property
    def is_truthy(self) -> bool:
        """Whether this value is truthy in Sass."""
        return False
    
    @property
    def separator(self) -> Optional[str]:
        """The separator for this value if it's a list, None otherwise."""
        return None
    
    @property
    def has_brackets(self) -> bool:
        """Whether this value has brackets if it's a list, False otherwise."""
        return False
    
    def __eq__(self, other: object) -> bool:
        """Check if this value equals another value."""
        # Use identity comparison for singleton
        return self is other
    
    def __hash__(self) -> int:
        """Return the hash of this value."""
        return hash(None)
    
    def __str__(self) -> str:
        """Return the string representation of this value."""
        return "null"
    
    def __repr__(self) -> str:
        """Return the debug representation of this value."""
        return "SassNull()"


# Create singleton instance
sass_null = SassNull()

# Prevent further construction
SassNull._construction_allowed = False
