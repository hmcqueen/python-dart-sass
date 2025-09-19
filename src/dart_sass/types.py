"""
Type definitions for Sass embedded host.
"""

from typing import Any, Dict, List, Optional, Union, Protocol, runtime_checkable
from typing_extensions import TypedDict


class CompileResult(TypedDict):
    """Result of a Sass compilation."""
    css: str
    loaded_urls: List[str]
    source_map: Optional[Union[str, Dict[str, Any]]]  # Can be parsed JSON object or string


class SourceSpan(TypedDict):
    """Information about a source location."""
    start: Dict[str, Any]
    end: Dict[str, Any]
    url: Optional[str]
    text: str
    context: Optional[str]


@runtime_checkable
class Importer(Protocol):
    """Protocol for custom importers."""
    
    def canonicalize(self, url: str, context: Dict[str, Any]) -> Optional[str]:
        """Canonicalize an import URL."""
        ...
    
    def load(self, canonical_url: str) -> Optional[Dict[str, Any]]:
        """Load the contents of a canonicalized URL."""
        ...


@runtime_checkable  
class CustomFunction(Protocol):
    """Protocol for custom Sass functions."""
    
    def __call__(self, *args: Any) -> Any:
        """Call the custom function."""
        ...


# Type aliases for common types
SassValue = Any  # Will be replaced with proper Value union type
Options = Dict[str, Any]
StringOptions = Dict[str, Any]
