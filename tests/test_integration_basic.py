"""
Basic integration tests for the embedded Sass compiler.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from dart_sass.compiler.async_compiler import AsyncCompiler, init_async_compiler
from dart_sass.exception import CompileException


class TestBasicIntegration:
    """Basic integration test cases."""
    
    @pytest.mark.asyncio
    async def test_async_compiler_initialization(self):
        """Test that AsyncCompiler can be initialized."""
        with patch('dart_sass.compiler.async_compiler.get_compiler_command') as mock_get_command:
            mock_get_command.return_value = ['mock-sass', '--embedded']
            
            with patch('asyncio.create_subprocess_exec') as mock_subprocess:
                # Mock the subprocess
                mock_process = AsyncMock()
                mock_process.stdin = AsyncMock()
                mock_process.stdout = AsyncMock()
                mock_process.stderr = AsyncMock()
                mock_process.wait = AsyncMock(return_value=0)
                mock_subprocess.return_value = mock_process
                
                # Create compiler using proper init function (like Node.js)
                compiler = await init_async_compiler()
                
                # Should not raise an exception
                assert compiler is not None
                assert not compiler._disposed
                
                # Clean up
                await compiler.dispose()
    
    @pytest.mark.asyncio
    async def test_async_compiler_no_executable_found(self):
        """Test error handling when no Sass executable is found."""
        with patch('dart_sass.compiler.async_compiler.get_compiler_command') as mock_get_command:
            mock_get_command.side_effect = RuntimeError("No compiler found")
            
            with pytest.raises(CompileException, match="No compiler found"):
                await init_async_compiler()
    
    @pytest.mark.asyncio
    async def test_async_compiler_process_start_failure(self):
        """Test error handling when process fails to start."""
        with patch('dart_sass.compiler.async_compiler.get_compiler_command') as mock_get_command:
            mock_get_command.return_value = ['mock-sass', '--embedded']
            
            with patch('asyncio.create_subprocess_exec') as mock_subprocess:
                mock_subprocess.side_effect = OSError("Failed to start process")
                
                # The error should occur during init_async_compiler since it calls _initialize_if_needed
                with pytest.raises(CompileException, match="Failed to start compiler process"):
                    compiler = await init_async_compiler()
                    # If we get here, try to trigger initialization
                    await compiler.compile_string_async('.test { color: red; }')
    
    @pytest.mark.asyncio
    async def test_async_compiler_dispose(self):
        """Test compiler disposal."""
        with patch('dart_sass.compiler.async_compiler.get_compiler_command') as mock_get_command:
            mock_get_command.return_value = ['mock-sass', '--embedded']
            
            with patch('asyncio.create_subprocess_exec') as mock_subprocess:
                # Mock the subprocess
                mock_process = AsyncMock()
                mock_process.stdin = AsyncMock()
                mock_process.stdout = AsyncMock()
                mock_process.stderr = AsyncMock()
                mock_process.wait = AsyncMock(return_value=0)
                mock_process.terminate = MagicMock()
                mock_process.kill = MagicMock()
                mock_subprocess.return_value = mock_process
                
                # Create and initialize compiler using proper init function
                compiler = await init_async_compiler()
                
                # Dispose
                await compiler.dispose()
                
                assert compiler._disposed
                
                # Should handle multiple dispose calls gracefully
                await compiler.dispose()
    
    def test_cli_tool_import(self):
        """Test that the CLI tool can be imported."""
        from dart_sass.cli import main
        assert callable(main)
    
    def test_compiler_path_detection(self):
        """Test that compiler path detection works."""
        from dart_sass.compiler_path import _detect_platform, _get_compiler_module_name
        
        platform = _detect_platform()
        assert isinstance(platform, str)
        assert '-' in platform  # Should be like 'linux-x64'
        
        module_name = _get_compiler_module_name()
        assert module_name.startswith('sass-embedded-')
        assert platform in module_name
