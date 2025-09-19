"""
CanonicalizeContext for Sass importers.
"""

from typing import Optional
from urllib.parse import urlparse


class CanonicalizeContext:
    """
    Context object passed to importer canonicalize() and findFileUrl() methods.
    
    This matches the Sass specification exactly.
    """
    
    def __init__(self, containing_url: Optional[str] = None, from_import: bool = False):
        """
        Initialize the canonicalize context.
        
        Args:
            containing_url: The canonical URL of the current source file, if any
            from_import: True if this is from an @import rule, False for @use/@forward
        """
        self._containing_url = containing_url
        self._from_import = from_import
        self._containing_url_accessed = False
    
    @property
    def from_import(self) -> bool:
        """True if the importer is being run for an @import, False otherwise."""
        return self._from_import
    
    @property
    def containing_url(self) -> Optional[str]:
        """The canonical URL of the current source file, if it has one."""
        self._containing_url_accessed = True
        return self._containing_url
    
    @property
    def containing_url_accessed(self) -> bool:
        """Whether the containing_url property has been accessed (for protocol optimization)."""
        return self._containing_url_accessed
