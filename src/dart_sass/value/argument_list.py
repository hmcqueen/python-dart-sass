"""
Argument list value type for Sass.
"""

from typing import Dict, List, Optional, Iterator
from .base import Value
from .list import SassList, ListSeparator


class SassArgumentList(SassList):
    """
    A Sass argument list value.
    
    This is a special type of list that represents the arguments passed to
    a function or mixin. It can contain both positional and keyword arguments.
    """
    
    def __init__(
        self,
        contents: List[Value],
        keywords: Optional[Dict[str, Value]] = None,
        separator: ListSeparator = ListSeparator.COMMA,
    ):
        """
        Initialize a SassArgumentList.
        
        Args:
            contents: The positional arguments
            keywords: The keyword arguments
            separator: The separator between elements
        """
        super().__init__(contents, separator, brackets=False)
        self._keywords = keywords or {}
    
    @property
    def keywords(self) -> Dict[str, Value]:
        """The keyword arguments."""
        return self._keywords.copy()
    
    def get_keyword(self, name: str) -> Optional[Value]:
        """
        Get a keyword argument by name.
        
        Args:
            name: The keyword name
            
        Returns:
            The keyword value or None if not found
        """
        return self._keywords.get(name)
    
    def has_keyword(self, name: str) -> bool:
        """
        Check if a keyword argument exists.
        
        Args:
            name: The keyword name
            
        Returns:
            True if the keyword exists
        """
        return name in self._keywords
    
    def __eq__(self, other: object) -> bool:
        """Check if this value equals another value."""
        if not isinstance(other, SassArgumentList):
            return False
        return (
            super().__eq__(other) and
            self._keywords == other._keywords
        )
    
    def __hash__(self) -> int:
        """Return the hash of this value."""
        return hash((super().__hash__(), tuple(sorted(self._keywords.items()))))
    
    def __str__(self) -> str:
        """Return the string representation of this value."""
        # For display purposes, argument lists look like regular lists
        return super().__str__()
    
    def __repr__(self) -> str:
        """Return the debug representation of this value."""
        return f"SassArgumentList({self._contents!r}, {self._keywords!r}, {self._separator!r})"
