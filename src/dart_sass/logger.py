"""
Logger interface for Sass embedded host.
"""

from abc import ABC, abstractmethod
from typing import Optional


class Logger(ABC):
    """
    An interface for loggers that receive messages from Sass.
    """
    
    @abstractmethod
    def debug(self, message: str, span: Optional[object] = None) -> None:
        """
        Log a debug message.
        
        Args:
            message: The debug message
            span: Optional source span information
        """
        pass
    
    @abstractmethod
    def warn(self, message: str, span: Optional[object] = None, deprecation: bool = False) -> None:
        """
        Log a warning message.
        
        Args:
            message: The warning message
            span: Optional source span information
            deprecation: Whether this is a deprecation warning
        """
        pass


class _SilentLogger(Logger):
    """
    A logger that silently discards all messages.
    
    This matches the Node.js Logger.silent functionality.
    """
    
    def debug(self, message: str, span: Optional[object] = None) -> None:
        """Silently discard debug messages."""
        pass
    
    def warn(self, message: str, span: Optional[object] = None, deprecation: bool = False) -> None:
        """Silently discard warning messages."""
        pass


# Create the silent logger instance like Node.js Logger.silent
Logger.silent = _SilentLogger()
