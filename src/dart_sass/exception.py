"""
Exception types for Sass embedded host.
"""

from typing import Optional


class Exception(Exception):
    """
    An exception thrown by Sass compilation.
    
    This is the base exception type for all Sass-related errors.
    """
    
    def __init__(self, message: str, span: Optional[object] = None):
        """
        Initialize a Sass exception.
        
        Args:
            message: The error message
            span: Optional source span information
        """
        super().__init__(message)
        self.span = span
        
    def __str__(self) -> str:
        """Return the string representation of the exception."""
        return super().__str__()


class CompileException(Exception):
    """
    An exception thrown during Sass compilation.
    
    Contains detailed error information including source location,
    stack trace, and formatted error messages.
    """
    
    def __init__(self, message: str, span=None, stack_trace: str = None, formatted: str = None):
        """
        Initialize a CompileException.
        
        Args:
            message: Basic error message
            span: Source span information (line, column, file)
            stack_trace: Sass compilation stack trace
            formatted: Formatted error message with visual indicators
        """
        super().__init__(message)
        self.span = span
        self.stack_trace = stack_trace
        self.formatted = formatted
        
    def __str__(self) -> str:
        """Return the best available error message."""
        # Prefer formatted message (includes line numbers, visual indicators)
        if self.formatted:
            return self.formatted
        # Fall back to basic message
        return super().__str__()


class ProtocolException(Exception):
    """
    An exception thrown due to protocol communication errors.
    """
    pass
