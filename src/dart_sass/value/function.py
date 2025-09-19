"""
Function value type for Sass.
"""

from typing import Optional, Callable, Any, List
from .base import Value


class SassFunction(Value):
    """
    A Sass function value.
    
    This represents a function that can be called from Sass code.
    """
    
    def __init__(self, name: str, callback: Optional[Callable[..., Any]] = None):
        """
        Initialize a SassFunction.
        
        Args:
            name: The function name
            callback: The Python function to call
        """
        self._name = name
        self._callback = callback
    
    @property
    def name(self) -> str:
        """The function name."""
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
    
    def __call__(self, *args: Value) -> Value:
        """
        Call the function with the given arguments.
        
        Args:
            *args: The function arguments
            
        Returns:
            The function result
            
        Raises:
            ValueError: If no callback is set or the callback fails
        """
        if self._callback is None:
            raise ValueError(f"Function {self._name} has no callback")
        
        try:
            return self._callback(*args)
        except Exception as e:
            raise ValueError(f"Error calling function {self._name}: {e}") from e
    
    def __eq__(self, other: object) -> bool:
        """Check if this value equals another value."""
        if not isinstance(other, SassFunction):
            return False
        return self._name == other._name and self._callback == other._callback
    
    def __hash__(self) -> int:
        """Return the hash of this value."""
        return hash((self._name, self._callback))
    
    def __str__(self) -> str:
        """Return the string representation of this value."""
        return f"get-function(\"{self._name}\")"
    
    def __repr__(self) -> str:
        """Return the debug representation of this value."""
        return f"SassFunction({self._name!r}, {self._callback!r})"
