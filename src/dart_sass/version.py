"""
Version information for Sass embedded host.
"""

from typing import NamedTuple


# Protocol version - should match the embedded Sass protocol version we support
__protocol_version__ = "3.2.0"


class Version(NamedTuple):
    """
    A semantic version number.
    """
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        """Return the string representation of the version."""
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @classmethod
    def parse(cls, version_string: str) -> "Version":
        """
        Parse a version string into a Version object.
        
        Args:
            version_string: A version string like "1.2.3"
            
        Returns:
            A Version object
            
        Raises:
            ValueError: If the version string is invalid
        """
        parts = version_string.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version string: {version_string}")
        
        try:
            major, minor, patch = map(int, parts)
            return cls(major, minor, patch)
        except ValueError as e:
            raise ValueError(f"Invalid version string: {version_string}") from e
