"""
Mixin value type for Sass.
"""

from typing import Optional, Callable, Any
from .base import Value


class SassMixin(Value):
    """
    A Sass mixin value.
    
    This represents a mixin that can be included in Sass code.
    """
    
    def __init__(self, name: str, callback: Optional[Callable[..., Any]] = None):
        """
        Initialize a SassMixin.
        
        Args:
            name: The mixin name
            callback: The Python function to call
        """
        self._name = name
        self._callback = callback
    
    @property
    def name(self) -> str:
        """The mixin name."""
        return self._name
    
    @property
    def callback(self) -> Optional[Callable[..., Any]]:
        """The Python callback function."""
        return self._callback
    
    @property
    def is_truthy(self) -> bool:
        """Whether this value is truthy in Sass."""
        return True
    
    @property
    def separator(self) -> Optional[str]:
        """The separator for this value if it's a list, None otherwise."""
        return None
    
    @property
    def has_brackets(self) -> bool:
        """Whether this value has brackets if it's a list, False otherwise."""
        return False
    
    def __call__(self, *args: Value) -> None:
        """
        Call the mixin with the given arguments.
        
        Args:
            *args: The mixin arguments
            
        Raises:
            ValueError: If no callback is set or the callback fails
        """
        if self._callback is None:
            raise ValueError(f"Mixin {self._name} has no callback")
        
        try:
            self._callback(*args)
        except Exception as e:
            raise ValueError(f"Error calling mixin {self._name}: {e}") from e
    
    def __eq__(self, other: object) -> bool:
        """Check if this value equals another value."""
        if not isinstance(other, SassMixin):
            return False
        return self._name == other._name and self._callback == other._callback
    
    def __hash__(self) -> int:
        """Return the hash of this value."""
        return hash((self._name, self._callback))
    
    def __str__(self) -> str:
        """Return the string representation of this value."""
        return f"get-mixin(\"{self._name}\")"
    
    def __repr__(self) -> str:
        """Return the debug representation of this value."""
        return f"SassMixin({self._name!r}, {self._callback!r})"
