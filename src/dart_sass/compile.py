"""
Main compilation functions for Sass embedded host.
"""

from typing import Optional
from .compiler.async_compiler import init_async_compiler
from .compiler.sync_compiler import init_sync_compiler
from .compiler.utils import CompileOptions, StringCompileOptions
from .types import CompileResult

__all__ = ["compile", "compile_string", "compile_async", "compile_string_async"]


def compile(
    path: str,
    options: Optional[CompileOptions] = None,
) -> CompileResult:
    """
    Synchronously compile a Sass file to CSS.
    
    Args:
        path: The path to the Sass file to compile
        options: Compilation options
        
    Returns:
        CompileResult containing the compiled CSS and metadata
    """
    compiler = init_sync_compiler()
    try:
        return compiler.compile(path, options)
    finally:
        compiler.dispose()


def compile_string(
    source: str,
    options: Optional[StringCompileOptions] = None,
) -> CompileResult:
    """
    Synchronously compile a Sass string to CSS.
    
    Args:
        source: The Sass source code to compile
        options: Compilation options
        
    Returns:
        CompileResult containing the compiled CSS and metadata
    """
    compiler = init_sync_compiler()
    try:
        return compiler.compile_string(source, options)
    finally:
        compiler.dispose()


async def compile_async(
    path: str,
    options: Optional[CompileOptions] = None,
) -> CompileResult:
    """
    Asynchronously compile a Sass file to CSS.
    
    Args:
        path: The path to the Sass file to compile
        options: Compilation options
        
    Returns:
        CompileResult containing the compiled CSS and metadata
    """
    compiler = await init_async_compiler()
    try:
        return await compiler.compile_async(path, options)
    finally:
        await compiler.dispose()


async def compile_string_async(
    source: str,
    options: Optional[StringCompileOptions] = None,
) -> CompileResult:
    """
    Asynchronously compile a Sass string to CSS.
    
    Args:
        source: The Sass source code to compile
        options: Compilation options
        
    Returns:
        CompileResult containing the compiled CSS and metadata
    """
    compiler = await init_async_compiler()
    try:
        return await compiler.compile_string_async(source, options)
    finally:
        await compiler.dispose()
