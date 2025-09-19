"""
Utility functions for the embedded Sass host.
"""

import os
import platform
from pathlib import Path
from urllib.parse import quote
from typing import TypeVar, Union, Awaitable, Callable, Any, Optional
from .exception import CompileException, ProtocolException
from .vendor import embedded_sass_pb2 as proto

T = TypeVar('T')

# Type alias for values that can be either sync or async
PromiseOr = Union[T, Awaitable[T]]


def protofy_syntax(syntax: Optional[str]) -> proto.Syntax:
    """
    Convert a syntax string to protobuf Syntax enum.
    
    This matches the Node.js utils.protofySyntax() function.
    
    Args:
        syntax: The syntax string ('scss', 'sass', 'css')
        
    Returns:
        The corresponding protobuf Syntax enum value
    """
    if not syntax or syntax == 'scss':
        return proto.Syntax.SCSS
    elif syntax == 'sass':
        return proto.Syntax.INDENTED
    elif syntax == 'css':
        return proto.Syntax.CSS
    else:
        raise ValueError(f"Unknown syntax: {syntax}")


def compiler_error(message: str) -> CompileException:
    """
    Create a compiler error (match Node.js compilerError).
    
    Args:
        message: The error message
        
    Returns:
        A CompileException with proper message format
    """
    return CompileException(f"Compiler caused error: {message}.")


def host_error(message: str) -> ProtocolException:
    """
    Create a host protocol error (match Node.js hostError).
    
    Args:
        message: The error message
        
    Returns:
        A ProtocolException with proper message format
    """
    return ProtocolException(f"Compiler reported error: {message}.")


def then_or(value: PromiseOr[T], callback: Callable[[T], Any]) -> Any:
    """
    Apply a callback to a value that might be a promise.
    
    This matches the Node.js thenOr utility function exactly.
    
    Args:
        value: The value or promise
        callback: The callback to apply
        
    Returns:
        The result of the callback, possibly wrapped in a promise
    """
    if hasattr(value, '__await__'):
        # It's awaitable - equivalent to promiseOrValue.then(callback)
        async def async_wrapper():
            result = await value
            return callback(result)
        return async_wrapper()
    else:
        # It's a regular value - equivalent to callback(promiseOrValue)
        return callback(value)


def catch_or(promise_or_value_callback: Callable[[], PromiseOr[T]], error_callback: Callable[[Exception], Any]) -> Any:
    """
    Execute a callback and handle both sync and async errors.
    
    This matches the Node.js catchOr utility function exactly.
    
    Args:
        promise_or_value_callback: Function that returns a value or promise
        error_callback: Function to handle errors
        
    Returns:
        The result of the callback or error handler, possibly wrapped in a promise
    """
    try:
        result = promise_or_value_callback()
        # If result is awaitable, handle async errors
        if hasattr(result, '__await__'):
            async def async_wrapper():
                try:
                    return await result
                except Exception as e:
                    return error_callback(e)
            return async_wrapper()
        else:
            # Sync result, return directly
            return result
    except Exception as e:
        # Sync error, handle immediately
        return error_callback(e)


def path_to_url_string(path: str) -> str:
    """
    Converts a (possibly relative) path on the local filesystem to a URL string.
    
    This follows the Node.js pathToFileURL behavior for consistency with the
    reference implementation.
    
    Args:
        path: The file path to convert
        
    Returns:
        URL-encoded path string
    """
    import re
    
    if os.path.isabs(path):
        # For absolute paths, use pathlib to convert to file URL
        return Path(path).as_uri()
    
    # For relative paths, percent encode like pathToFileURL
    # The Node.js implementation uses encodeURI with specific replacements
    
    # Check if this is already properly percent-encoded
    # Valid percent encoding is %XX where XX are hex digits
    percent_encoded_pattern = re.compile(r'%[0-9A-Fa-f]{2}')
    if percent_encoded_pattern.search(path):
        # This appears to be already percent-encoded, preserve it
        # Just handle platform-specific separators
        file_url = path
        if platform.system() == 'Windows':
            file_url = file_url.replace('%5C', '/')
        return file_url
    
    # For non-percent-encoded paths, encode special characters
    # Use quote with safe characters matching Node.js behavior
    file_url = quote(path, safe='-._~')
    
    # Handle platform-specific path separators
    if platform.system() == 'Windows':
        # Convert backslashes to forward slashes for URLs
        file_url = file_url.replace('%5C', '/')
    
    return file_url
