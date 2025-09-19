"""
Embedded Sass Host for Python

This package is a Python wrapper around the Embedded Dart Sass compiler.
It provides the same API as the sass package but uses the embedded protocol
for better performance.
"""

from .compiler.async_compiler import init_async_compiler, AsyncCompiler
from .compiler.sync_compiler import init_sync_compiler, SyncCompiler
from .function_registry import FunctionRegistry
from .importer_registry import ImporterResult
from .canonicalize_context import CanonicalizeContext
from .exception import CompileException
from .types import CompileResult
from .value import (
    ListSeparator,
    SassList,
    SassArgumentList,
    SassBoolean,
    sass_false,
    sass_true,
    SassColor,
    SassFunction,
    SassMap,
    SassMixin,
    SassNumber,
    SassString,
    Value,
    sass_null,
    SassCalculation,
)

# Package metadata
__version__ = "1.0.0"
__protocol_version__ = "3.2.0"
__compiler_version__ = "1.90.0"

info = f"sass-embedded\t{__version__}"

# Sass value constants
TRUE = sass_true
FALSE = sass_false
NULL = sass_null


def compile(path: str, options: dict = None) -> CompileResult:
    """
    Compile a Sass file to CSS synchronously.
    
    Args:
        path: Path to the Sass file to compile
        options: Compilation options
        
    Returns:
        CompileResult containing the compiled CSS and metadata
    """
    compiler = init_sync_compiler()
    try:
        return compiler.compile(path, options)
    finally:
        compiler.dispose()


def compile_string(source: str, options: dict = None) -> CompileResult:
    """
    Compile a Sass string to CSS synchronously.
    
    Args:
        source: Sass source code to compile
        options: Compilation options
        
    Returns:
        CompileResult containing the compiled CSS and metadata
    """
    compiler = init_sync_compiler()
    try:
        return compiler.compile_string(source, options)
    finally:
        compiler.dispose()


async def compile_async(path: str, options: dict = None) -> CompileResult:
    """
    Compile a Sass file to CSS asynchronously.
    
    Args:
        path: Path to the Sass file to compile
        options: Compilation options
        
    Returns:
        CompileResult containing the compiled CSS and metadata
    """
    compiler = await init_async_compiler()
    try:
        return await compiler.compile_async(path, options)
    finally:
        await compiler.dispose()


async def compile_string_async(source: str, options: dict = None) -> CompileResult:
    """
    Compile a Sass string to CSS asynchronously.
    
    Args:
        source: Sass source code to compile
        options: Compilation options
        
    Returns:
        CompileResult containing the compiled CSS and metadata
    """
    compiler = await init_async_compiler()
    try:
        return await compiler.compile_string_async(source, options)
    finally:
        await compiler.dispose()


__all__ = [
    # Core compilation functions
    "compile",
    "compile_string", 
    "compile_async",
    "compile_string_async",
    
    # Compiler classes
    "init_async_compiler",
    "AsyncCompiler", 
    "init_sync_compiler",
    "SyncCompiler",
    
    # Function and importer registration
    "FunctionRegistry",
    "ImporterResult",
    "CanonicalizeContext",
    
    # Value types
    "ListSeparator",
    "SassList",
    "SassArgumentList", 
    "SassBoolean",
    "sass_false",
    "sass_true",
    "SassColor",
    "SassFunction",
    "SassMap",
    "SassMixin", 
    "SassNumber",
    "SassString",
    "Value",
    "sass_null",
    "SassCalculation",
    
    # Types and exceptions
    "CompileResult",
    "CompileException",
    
    # Sass value constants
    "TRUE",
    "FALSE", 
    "NULL",
    
    # Package info
    "info",
    "__version__",
    "__protocol_version__",
    "__compiler_version__",
]
