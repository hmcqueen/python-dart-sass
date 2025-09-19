"""
Boolean value type for Sass.
"""

from typing import Optional
from .base import Value


class SassBoolean(Value):
    """
    A Sass boolean value.
    
    This is an abstract class that cannot be directly instantiated.
    Use the provided sass_true and sass_false singleton instances.
    """
    
    _construction_allowed = True
    
    def __init__(self, value: bool):
        """
        Initialize a SassBoolean.
        
        Args:
            value: The boolean value
            
        Raises:
            TypeError: If construction is not allowed (after singletons are created)
        """
        if not SassBoolean._construction_allowed:
            raise TypeError(
                "SassBoolean() isn't allowed.\n"
                "Use sass_true or sass_false instead."
            )
        self._value = value
    
    @property
    def value(self) -> bool:
        """The underlying boolean value."""
        return self._value
    
    @property
    def is_truthy(self) -> bool:
        """Whether this value is truthy in Sass."""
        return self._value
    
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
        # Use identity comparison for singletons
        return self is other
    
    def __hash__(self) -> int:
        """Return the hash of this value."""
        return hash(self._value)
    
    def __str__(self) -> str:
        """Return the string representation of this value."""
        return "true" if self._value else "false"
    
    def __repr__(self) -> str:
        """Return the debug representation of this value."""
        return f"SassBoolean({self._value})"


# Create singleton instances
sass_true = SassBoolean(True)
sass_false = SassBoolean(False)

# Prevent further construction
SassBoolean._construction_allowed = False
