"""
List value type for Sass.
"""

from enum import Enum
from typing import List, Optional, Iterator, Union
from .base import Value


class ListSeparator(Enum):
    """The separator for a Sass list."""
    COMMA = "comma"
    SPACE = "space"
    SLASH = "slash"
    UNDECIDED = "undecided"


class SassList(Value):
    """
    A Sass list value.
    
    Lists can be separated by commas, spaces, or slashes, and can optionally
    have square brackets.
    """
    
    def __init__(
        self,
        contents: List[Value],
        separator: ListSeparator = ListSeparator.COMMA,
        brackets: bool = False,
    ):
        """
        Initialize a SassList.
        
        Args:
            contents: The list elements
            separator: The separator between elements
            brackets: Whether the list has square brackets
        """
        self._contents = list(contents)
        self._separator = separator
        self._brackets = brackets
    
    @property
    def contents(self) -> List[Value]:
        """The list elements."""
        return self._contents.copy()
    
    @property
    def separator_enum(self) -> ListSeparator:
        """The separator as an enum."""
        return self._separator
    
    @property
    def separator(self) -> str:
        """The separator as a string (matches Node.js separator property)."""
        match self._separator:
            case ListSeparator.COMMA:
                return ','
            case ListSeparator.SPACE:
                return ' '
            case ListSeparator.SLASH:
                return '/'
            case ListSeparator.UNDECIDED:
                return None
            case _:
                return ','
    
    @property
    def has_brackets(self) -> bool:
        """Whether this list has brackets (matches Node.js hasBrackets property)."""
        return self._brackets
    
    @property
    def is_truthy(self) -> bool:
        """Lists are always truthy in Sass."""
        return True
    
    def __len__(self) -> int:
        """The number of elements in the list."""
        return len(self._contents)
    
    def __iter__(self) -> Iterator[Value]:
        """Iterate over the list elements."""
        return iter(self._contents)
    
    def __getitem__(self, index: int) -> Value:
        """Get an element by index."""
        return self._contents[index]
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, SassList):
            return False
        return (
            self._contents == other._contents and
            self._separator == other._separator and
            self._brackets == other._brackets
        )
    
    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash((tuple(self._contents), self._separator, self._brackets))
    
    def __str__(self) -> str:
        """String representation matching Sass output."""
        if not self._contents:
            return "[]" if self._brackets else "()"
        
        sep_str = self.separator or " "
        content_str = sep_str.join(str(item) for item in self._contents)
        
        if self._brackets:
            return f"[{content_str}]"
        elif len(self._contents) == 1 and self._separator == ListSeparator.COMMA:
            return f"({content_str},)"
        else:
            return content_str
    
    def __repr__(self) -> str:
        """Python representation."""
        return f"SassList({self._contents!r}, separator={self._separator!r}, brackets={self._brackets})"
