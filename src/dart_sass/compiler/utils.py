"""
Compiler utilities for handling log events and other compiler operations.
"""

import json
import os
import sys
from typing import Dict, Any, Optional, Callable
from ..vendor import embedded_sass_pb2 as proto
from ..dispatcher import Dispatcher
from ..message_transformer import MessageTransformer
from ..types import CompileResult
from ..exception import CompileException
from ..utils import compiler_error, protofy_syntax
from ..deprecations import get_deprecation_ids, valid_deprecation_id
from ..deprotofy_span import deprotofy_source_span
from ..logger import Logger

# Type aliases for options
CompileOptions = Dict[str, Any]
StringCompileOptions = Dict[str, Any]


def _supports_color() -> bool:
    """
    Detect if the terminal supports color output.
    
    This matches the Node.js supportsColor.stdout functionality.
    
    Returns:
        True if terminal supports color, False otherwise
    """
    # Check if we're in a TTY
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    
    # Check environment variables
    if 'NO_COLOR' in os.environ:
        return False
    
    if 'FORCE_COLOR' in os.environ:
        return True
    
    # Check TERM environment variable
    term = os.environ.get('TERM', '').lower()
    if term in ('dumb', 'unknown'):
        return False
    
    # Most modern terminals support color
    if term:
        return True
    
    # Default to False if we can't determine
    return False


def create_dispatcher(
    compilation_id: int,
    message_transformer: MessageTransformer,
    handlers: Dict[str, Callable]
) -> Dispatcher:
    """
    Creates a dispatcher that dispatches messages from the given message transformer.
    
    Args:
        compilation_id: The compilation ID for this dispatcher
        message_transformer: The message transformer to use
        handlers: Dictionary of callback handlers for different message types
        
    Returns:
        A new Dispatcher instance
    """
    return Dispatcher(
        compilation_id,
        message_transformer.outbound_messages,
        lambda message: message_transformer.write_inbound_message(message),
        handlers,
    )


def _new_compile_request(
    importers,  # ImporterRegistry type - avoiding circular import for now
    options: Optional[Dict[str, Any]] = None
) -> proto.InboundMessage.CompileRequest:
    """
    Creates a compilation request for the given options without adding any input-specific options.
    
    This matches the Node.js newCompileRequest() internal function.
    
    Args:
        importers: The importer registry
        options: Compilation options
        
    Returns:
        A protobuf CompileRequest
    """
    request = proto.InboundMessage.CompileRequest()
    
    # Set importers (like Node.js: importers: importers.importers)
    if importers and hasattr(importers, 'importers'):
        request.importers.extend(importers.importers)
    
    # Set global functions
    if options and 'functions' in options:
        request.global_functions.extend(options['functions'].keys())
    
    # Set source map options
    request.source_map = bool(options and options.get('source_map', False))
    request.source_map_include_sources = bool(options and options.get('source_map_include_sources', False))
    
    # Set alert options - use color detection like Node.js supportsColor.stdout
    request.alert_color = options.get('alert_color', _supports_color()) if options else _supports_color()
    request.alert_ascii = bool(options and options.get('alert_ascii', False))
    
    # Set other options
    request.quiet_deps = bool(options and options.get('quiet_deps', False))
    request.verbose = bool(options and options.get('verbose', False))
    request.charset = bool(options and options.get('charset', True))
    request.silent = bool(options and options.get('logger') is Logger.silent)
    
    # Set deprecation options using the deprecation functions
    if options:
        request.fatal_deprecation.extend(get_deprecation_ids(options.get('fatal_deprecations', [])))
        request.silence_deprecation.extend(get_deprecation_ids(options.get('silence_deprecations', [])))
        request.future_deprecation.extend(get_deprecation_ids(options.get('future_deprecations', [])))
    
    # Set output style
    style = options.get('style', 'expanded') if options else 'expanded'
    if style == 'expanded':
        request.style = proto.OutputStyle.EXPANDED
    elif style == 'compressed':
        request.style = proto.OutputStyle.COMPRESSED
    else:
        raise ValueError(f"Unknown options.style: \"{style}\"")
    
    return request


def new_compile_path_request(
    path: str,
    importers,  # ImporterRegistry type - avoiding circular import for now
    options: Optional[Dict[str, Any]] = None
) -> proto.InboundMessage.CompileRequest:
    """
    Creates a request for compiling a file.
    
    This matches the Node.js newCompilePathRequest() function exactly.
    
    Args:
        path: The path to the Sass file to compile
        importers: The importer registry
        options: Compilation options
        
    Returns:
        A protobuf CompileRequest for file compilation
    """
    abs_path = os.path.abspath(path)
    request = _new_compile_request(importers, options)
    request.path = abs_path  # Set path directly, not input.path
    return request


def new_compile_string_request(
    source: str,
    importers,  # ImporterRegistry type - avoiding circular import for now
    options: Optional[Dict[str, Any]] = None
) -> proto.InboundMessage.CompileRequest:
    """
    Creates a request for compiling a string.
    
    This matches the Node.js newCompileStringRequest() function exactly.
    
    Args:
        source: The Sass source code to compile
        importers: The importer registry
        options: Compilation options
        
    Returns:
        A protobuf CompileRequest for string compilation
    """
    string_input = proto.InboundMessage.CompileRequest.StringInput()
    string_input.source = source
    
    # Set syntax using protofy_syntax like Node.js
    string_input.syntax = protofy_syntax(options.get('syntax') if options else None)
    
    # Set URL if provided
    if options and 'url' in options:
        url = str(options['url'])
        if url:  # Set URL if provided
            string_input.url = url
    
    # Set importer if provided
    if options and 'importer' in options and options['importer']:
        if hasattr(importers, 'register'):
            string_input.importer.CopyFrom(importers.register(options['importer']))
    # Otherwise, compiler will set FileSystemImporter or NoOpImporter
    
    request = _new_compile_request(importers, options)
    request.string.CopyFrom(string_input)  # Set string directly, not input.string
    return request


def handle_compile_response(
    response: proto.OutboundMessage.CompileResponse
) -> CompileResult:
    """
    Converts a CompileResponse into a CompileResult.
    
    This matches the Node.js handleCompileResponse() function exactly.
    Throws a CompileException if the compilation failed.
    
    Args:
        response: The protobuf compile response
        
    Returns:
        A CompileResult with the compilation results
        
    Raises:
        CompileException: If the compilation failed
    """
    if response.HasField('success'):
        success = response.success
        
        # Build the result object with Python snake_case field names
        result: CompileResult = {
            'css': success.css,
            'loaded_urls': [url for url in response.loaded_urls],  # Keep as strings (more Pythonic)
        }
        
        # Handle source map - check if it exists and has content
        if hasattr(success, 'source_map') and success.source_map:
            try:
                result['source_map'] = json.loads(success.source_map)
            except json.JSONDecodeError:
                # If parsing fails, keep as string
                result['source_map'] = success.source_map
        else:
            result['source_map'] = None
        
        return result
        
    elif response.HasField('failure'):
        # Compilation failed - throw exception with full error details
        failure = response.failure
        
        # Extract all available error information
        message = failure.message
        formatted = failure.formatted if failure.formatted else None
        stack_trace = failure.stack_trace if failure.stack_trace else None
        span = failure.span if failure.HasField('span') else None
        
        raise CompileException(
            message=message,
            span=span, 
            stack_trace=stack_trace,
            formatted=formatted
        )
    else:
        # Empty response - this shouldn't happen
        raise compiler_error('Compiler sent empty CompileResponse.')


def handle_log_event(
    options: Optional[Dict[str, Any]],
    event: proto.OutboundMessage.LogEvent
) -> None:
    """
    Handles a log event according to options.
    
    This matches the Node.js handleLogEvent() function structure.
    
    Args:
        options: Compilation options that may include logger
        event: The log event from the compiler
    """
    if not event:
        return
    
    # Extract and process span information like Node.js
    span = deprotofy_source_span(event.span) if event.HasField('span') else None
    
    # Extract message and formatted text
    message = event.message
    formatted = event.formatted
    
    # Extract deprecation type like Node.js
    deprecation_type = None
    if hasattr(event, 'deprecation_type') and valid_deprecation_id(event.deprecation_type):
        deprecation_type = event.deprecation_type
    
    if event.type == proto.LogEventType.DEBUG:
        # Handle debug messages
        if options and 'logger' in options and options['logger'] and 'debug' in options['logger']:
            logger_debug = options['logger']['debug']
            debug_params = {}
            if span:
                debug_params['span'] = span
            logger_debug(message, debug_params)
        else:
            # Fallback to stderr with DEBUG prefix (more helpful than Node.js)
            print(f"DEBUG: {formatted}", file=__import__('sys').stderr)
    else:
        # Handle warnings and other log types
        if options and 'logger' in options and options['logger'] and 'warn' in options['logger']:
            logger_warn = options['logger']['warn']
            
            # Build parameters exactly like Node.js but with snake_case
            if deprecation_type:
                params = {
                    'deprecation': True,
                    'deprecation_type': deprecation_type  # snake_case
                }
            else:
                params = {'deprecation': False}
            
            if span:
                params['span'] = span
            
            # Handle stack trace
            if event.HasField('stack_trace') and event.stack_trace:
                params['stack'] = event.stack_trace
            
            logger_warn(message, params)
        else:
            # Fallback to stderr with WARNING prefix (more helpful than Node.js)
            print(f"WARNING: {formatted}", file=__import__('sys').stderr)
