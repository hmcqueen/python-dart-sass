"""
Base Value class for all Sass values.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Union


class Value(ABC):
    """
    The abstract base class for all Sass values.
    
    All Sass values are immutable and implement equality comparison.
    """
    
    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Check if this value equals another value."""
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        """Return the hash of this value."""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """Return the string representation of this value."""
        pass
    
    @abstractmethod
    def __repr__(self) -> str:
        """Return the debug representation of this value."""
        pass
    
    @property
    @abstractmethod
    def is_truthy(self) -> bool:
        """
        Whether this value is truthy in Sass.
        
        Only false and null are falsy in Sass.
        """
        pass
    
    @property
    @abstractmethod
    def separator(self) -> Optional[str]:
        """
        The separator for this value if it's a list, None otherwise.
        """
        pass
    
    @property
    @abstractmethod
    def has_brackets(self) -> bool:
        """
        Whether this value has brackets if it's a list, False otherwise.
        """
        pass
    
    def assert_boolean(self, name: Optional[str] = None) -> "SassBoolean":
        """
        Assert that this value is a boolean and return it.
        
        Args:
            name: The name of the parameter for error messages
            
        Returns:
            This value as a SassBoolean
            
        Raises:
            ValueError: If this value is not a boolean
        """
        from .boolean import SassBoolean
        if isinstance(self, SassBoolean):
            return self
        raise ValueError(f"{name or 'Value'} must be a boolean, was {type(self).__name__}")
    
    def assert_color(self, name: Optional[str] = None) -> "SassColor":
        """
        Assert that this value is a color and return it.
        
        Args:
            name: The name of the parameter for error messages
            
        Returns:
            This value as a SassColor
            
        Raises:
            ValueError: If this value is not a color
        """
        from .color import SassColor
        if isinstance(self, SassColor):
            return self
        raise ValueError(f"{name or 'Value'} must be a color, was {type(self).__name__}")
    
    def assert_function(self, name: Optional[str] = None) -> "SassFunction":
        """
        Assert that this value is a function and return it.
        
        Args:
            name: The name of the parameter for error messages
            
        Returns:
            This value as a SassFunction
            
        Raises:
            ValueError: If this value is not a function
        """
        from .function import SassFunction
        if isinstance(self, SassFunction):
            return self
        raise ValueError(f"{name or 'Value'} must be a function, was {type(self).__name__}")
    
    def assert_list(self, name: Optional[str] = None) -> "SassList":
        """
        Assert that this value is a list and return it.
        
        Args:
            name: The name of the parameter for error messages
            
        Returns:
            This value as a SassList
            
        Raises:
            ValueError: If this value is not a list
        """
        from .list import SassList
        if isinstance(self, SassList):
            return self
        raise ValueError(f"{name or 'Value'} must be a list, was {type(self).__name__}")
    
    def assert_map(self, name: Optional[str] = None) -> "SassMap":
        """
        Assert that this value is a map and return it.
        
        Args:
            name: The name of the parameter for error messages
            
        Returns:
            This value as a SassMap
            
        Raises:
            ValueError: If this value is not a map
        """
        from .map import SassMap
        if isinstance(self, SassMap):
            return self
        raise ValueError(f"{name or 'Value'} must be a map, was {type(self).__name__}")
    
    def assert_number(self, name: Optional[str] = None) -> "SassNumber":
        """
        Assert that this value is a number and return it.
        
        Args:
            name: The name of the parameter for error messages
            
        Returns:
            This value as a SassNumber
            
        Raises:
            ValueError: If this value is not a number
        """
        from .number import SassNumber
        if isinstance(self, SassNumber):
            return self
        raise ValueError(f"{name or 'Value'} must be a number, was {type(self).__name__}")
    
    def assert_string(self, name: Optional[str] = None) -> "SassString":
        """
        Assert that this value is a string and return it.
        
        Args:
            name: The name of the parameter for error messages
            
        Returns:
            This value as a SassString
            
        Raises:
            ValueError: If this value is not a string
        """
        from .string import SassString
        if isinstance(self, SassString):
            return self
        raise ValueError(f"{name or 'Value'} must be a string, was {type(self).__name__}")


# Forward declarations for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .boolean import SassBoolean
    from .color import SassColor
    from .function import SassFunction
    from .list import SassList
    from .map import SassMap
    from .number import SassNumber
    from .string import SassString
