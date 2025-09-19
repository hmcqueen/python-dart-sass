"""
Map value type for Sass.
"""

from typing import Dict, List, Optional, Iterator, Tuple, Union
from immutables import Map
from .base import Value


class SassMap(Value):
    """
    A Sass map value.
    
    Maps are immutable collections of key-value pairs where keys can be any
    Sass value type.
    """
    
    def __init__(self, contents: Union[Dict[Value, Value], List[Tuple[Value, Value]], Map[Value, Value]]):
        """
        Initialize a SassMap.
        
        Args:
            contents: The map contents as a dict, list of tuples, or immutable Map
        """
        if isinstance(contents, Map):
            self._contents = contents
        elif isinstance(contents, dict):
            self._contents = Map(contents)
        else:
            # List of tuples
            self._contents = Map(contents)
    
    @property
    def contents(self) -> Map[Value, Value]:
        """The map contents as an immutable Map."""
        return self._contents
    
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
    
    def __len__(self) -> int:
        """Return the number of key-value pairs in the map."""
        return len(self._contents)
    
    def __getitem__(self, key: Value) -> Value:
        """Get a value by key."""
        return self._contents[key]
    
    def __contains__(self, key: Value) -> bool:
        """Check if a key exists in the map."""
        return key in self._contents
    
    def __iter__(self) -> Iterator[Value]:
        """Iterate over the map keys."""
        return iter(self._contents)
    
    def keys(self) -> Iterator[Value]:
        """Return an iterator over the map keys."""
        return iter(self._contents)
    
    def values(self) -> Iterator[Value]:
        """Return an iterator over the map values."""
        return iter(self._contents.values())
    
    def items(self) -> Iterator[Tuple[Value, Value]]:
        """Return an iterator over the map key-value pairs."""
        return iter(self._contents.items())
    
    def get(self, key: Value, default: Optional[Value] = None) -> Optional[Value]:
        """Get a value by key with an optional default."""
        return self._contents.get(key, default)
    
    def set(self, key: Value, value: Value) -> "SassMap":
        """Return a new map with the key-value pair added or updated."""
        return SassMap(self._contents.set(key, value))
    
    def delete(self, key: Value) -> "SassMap":
        """Return a new map with the key removed."""
        return SassMap(self._contents.delete(key))
    
    def __eq__(self, other: object) -> bool:
        """Check if this value equals another value."""
        if not isinstance(other, SassMap):
            return False
        return self._contents == other._contents
    
    def __hash__(self) -> int:
        """Return the hash of this value."""
        return hash(self._contents)
    
    def __str__(self) -> str:
        """Return the string representation of this value."""
        if not self._contents:
            return "()"
        
        pairs = []
        for key, value in self._contents.items():
            pairs.append(f"{key}: {value}")
        
        return f"({', '.join(pairs)})"
    
    def __repr__(self) -> str:
        """Return the debug representation of this value."""
        return f"SassMap({dict(self._contents)!r})"
