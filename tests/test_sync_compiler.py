"""
Tests for synchronous compiler.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from dart_sass.compiler.sync_compiler import SyncCompiler, init_sync_compiler
from dart_sass.exception import CompileException


class TestSyncCompiler:
    """Test cases for synchronous compiler."""
    
    def test_init_sync_compiler(self):
        """Test sync compiler initialization."""
        # The new implementation uses AsyncCompiler internally
        with patch('dart_sass.compiler.sync_compiler.init_async_compiler') as mock_init_async:
            mock_async_compiler = MagicMock()
            mock_init_async.return_value = mock_async_compiler
            
            # Test initialization
            compiler = init_sync_compiler()
            assert compiler is not None
            assert isinstance(compiler, SyncCompiler)
            
            # Clean up
            compiler.dispose()
    
    def test_compile_disposed_error(self):
        """Test error when compiling with disposed compiler."""
        with patch('dart_sass.compiler.sync_compiler.init_async_compiler') as mock_init_async:
            mock_async_compiler = MagicMock()
            mock_init_async.return_value = mock_async_compiler
            
            compiler = init_sync_compiler()
            compiler.dispose()
            
            # Should raise error when trying to compile after disposal
            with pytest.raises(CompileException, match="disposed"):
                compiler.compile('test.scss')
    
    def test_compile_string_disposed_error(self):
        """Test error when compiling string with disposed compiler."""
        with patch('dart_sass.compiler.sync_compiler.init_async_compiler') as mock_init_async:
            mock_async_compiler = MagicMock()
            mock_init_async.return_value = mock_async_compiler
            
            compiler = init_sync_compiler()
            compiler.dispose()
            
            # Should raise error when trying to compile string after disposal
            with pytest.raises(CompileException, match="disposed"):
                compiler.compile_string('$color: blue;')
    
    def test_compiler_command_error(self):
        """Test error when compiler command cannot be found."""
        # Mock init_async_compiler to raise an exception during lazy initialization
        with patch('dart_sass.compiler.sync_compiler.init_async_compiler') as mock_init_async:
            mock_init_async.side_effect = CompileException("Compiler not found")
            
            compiler = init_sync_compiler()  # This won't fail yet
            
            # The error should occur when trying to compile (lazy initialization)
            with pytest.raises(CompileException, match="Compiler not found"):
                compiler.compile('test.scss')
    
    def test_process_start_error(self):
        """Test error when process fails to start."""
        # Mock init_async_compiler to raise an exception during lazy initialization
        with patch('dart_sass.compiler.sync_compiler.init_async_compiler') as mock_init_async:
            mock_init_async.side_effect = CompileException("Process failed to start")
            
            compiler = init_sync_compiler()  # This won't fail yet
            
            # The error should occur when trying to compile (lazy initialization)
            with pytest.raises(CompileException, match="Process failed to start"):
                compiler.compile_string('$color: blue;')
    
    def test_context_manager(self):
        """Test using sync compiler as context manager."""
        with patch('dart_sass.compiler.sync_compiler.init_async_compiler') as mock_init_async:
            mock_async_compiler = MagicMock()
            mock_init_async.return_value = mock_async_compiler
            
            # Test context manager usage
            with init_sync_compiler() as compiler:
                assert isinstance(compiler, SyncCompiler)
                assert not compiler._disposed
            
            # Should be disposed after context exit
            assert compiler._disposed
    
    def test_dispose_multiple_calls(self):
        """Test that multiple dispose calls are handled gracefully."""
        with patch('dart_sass.compiler.sync_compiler.init_async_compiler') as mock_init_async:
            mock_async_compiler = MagicMock()
            mock_init_async.return_value = mock_async_compiler
            
            compiler = init_sync_compiler()
            
            # First dispose should work
            compiler.dispose()
            assert compiler._disposed
            
            # Second dispose should not raise error
            compiler.dispose()
            assert compiler._disposed
    
    def test_compile_success(self):
        """Test successful compilation."""
        with patch('dart_sass.compiler.sync_compiler.init_async_compiler') as mock_init_async:
            # Mock async compiler and its methods
            mock_async_compiler = AsyncMock()
            mock_result = MagicMock()
            mock_result.css = ".test { color: blue; }"
            mock_async_compiler.compile.return_value = mock_result
            mock_init_async.return_value = mock_async_compiler
            
            compiler = init_sync_compiler()
            
            # Mock the event loop run method
            with patch.object(compiler._loop, 'run_until_complete') as mock_run:
                mock_run.return_value = mock_result
                
                result = compiler.compile('test.scss')
                assert result.css == ".test { color: blue; }"
            
            compiler.dispose()
    
    def test_compile_string_success(self):
        """Test successful string compilation."""
        with patch('dart_sass.compiler.sync_compiler.init_async_compiler') as mock_init_async:
            # Mock async compiler and its methods
            mock_async_compiler = AsyncMock()
            mock_result = MagicMock()
            mock_result.css = ".test { color: red; }"
            mock_async_compiler.compile_string.return_value = mock_result
            mock_init_async.return_value = mock_async_compiler
            
            compiler = init_sync_compiler()
            
            # Mock the event loop run method
            with patch.object(compiler._loop, 'run_until_complete') as mock_run:
                mock_run.return_value = mock_result
                
                result = compiler.compile_string('$color: red; .test { color: $color; }')
                assert result.css == ".test { color: red; }"
            
            compiler.dispose()
