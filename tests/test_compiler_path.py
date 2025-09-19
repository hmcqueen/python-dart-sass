"""
Tests for compiler path detection.
"""

import pytest
import os
import platform
from unittest.mock import patch, MagicMock
from dart_sass.compiler_path import (
    _detect_platform,
    _get_compiler_module_name,
    _find_dart_sass_executable,
    get_compiler_command,
)


class TestCompilerPath:
    """Test cases for compiler path detection."""
    
    def test_detect_platform(self):
        """Test platform detection."""
        with patch('platform.system') as mock_system, \
             patch('platform.machine') as mock_machine:
            
            # Test Linux x64
            mock_system.return_value = 'Linux'
            mock_machine.return_value = 'x86_64'
            assert _detect_platform() == 'linux-x64'
            
            # Test macOS ARM64
            mock_system.return_value = 'Darwin'
            mock_machine.return_value = 'arm64'
            assert _detect_platform() == 'darwin-arm64'
            
            # Test Windows x64
            mock_system.return_value = 'Windows'
            mock_machine.return_value = 'AMD64'
            assert _detect_platform() == 'win32-x64'
    
    def test_get_compiler_module_name(self):
        """Test compiler module name generation."""
        with patch('dart_sass.compiler_path._detect_platform') as mock_detect:
            mock_detect.return_value = 'linux-x64'
            assert _get_compiler_module_name() == 'sass-embedded-linux-x64'
            
            mock_detect.return_value = 'darwin-arm64'
            assert _get_compiler_module_name() == 'sass-embedded-darwin-arm64'
    
    def test_find_dart_sass_executable_with_dart(self):
        """Test finding Dart Sass with dart executable."""
        with patch('shutil.which') as mock_which, \
             patch('pathlib.Path.exists') as mock_exists:
            
            # Mock dart executable found
            mock_which.side_effect = lambda cmd: '/usr/bin/dart' if cmd == 'dart' else None
            
            # Mock snapshot file found
            mock_exists.return_value = True
            
            result = _find_dart_sass_executable()
            assert result is not None
            assert result[0] == '/usr/bin/dart'
            assert 'sass.snapshot' in result[1]
    
    def test_find_dart_sass_executable_with_sass(self):
        """Test finding Dart Sass with sass executable."""
        with patch('shutil.which') as mock_which, \
             patch('pathlib.Path.exists') as mock_exists:
            # Mock no dart executable found
            mock_which.side_effect = lambda cmd: '/usr/bin/sass' if cmd == 'sass' else None
            # Mock no snapshot files exist (so it falls back to sass executable)
            mock_exists.return_value = False
            
            result = _find_dart_sass_executable()
            assert result == ['/usr/bin/sass']
    
    def test_find_dart_sass_executable_not_found(self):
        """Test when no Dart Sass executable is found."""
        with patch('shutil.which') as mock_which, \
             patch('pathlib.Path.exists') as mock_exists:
            # Mock no executables found
            mock_which.return_value = None
            # Mock no snapshot files exist
            mock_exists.return_value = False
            
            result = _find_dart_sass_executable()
            assert result is None
            assert result is None
    
    def test_get_compiler_command_with_env_var(self):
        """Test getting compiler command from environment variable."""
        test_path = '/custom/path/to/sass'
        
        with patch.dict(os.environ, {'SASS_EMBEDDED_COMPILER_PATH': test_path}), \
             patch('os.path.isfile') as mock_isfile, \
             patch('os.access') as mock_access:
            
            mock_isfile.return_value = True
            mock_access.return_value = True
            
            result = get_compiler_command()
            assert result == [test_path]
    
    def test_get_compiler_command_env_var_invalid(self):
        """Test error when environment variable points to invalid file."""
        test_path = '/invalid/path/to/sass'
        
        with patch.dict(os.environ, {'SASS_EMBEDDED_COMPILER_PATH': test_path}), \
             patch('os.path.isfile') as mock_isfile:
            
            mock_isfile.return_value = False
            
            with pytest.raises(RuntimeError, match="SASS_EMBEDDED_COMPILER_PATH points to invalid executable"):
                get_compiler_command()
    
    def test_get_compiler_command_system_fallback(self):
        """Test falling back to system-installed Sass."""
        with patch.dict(os.environ, {}, clear=True), \
             patch('dart_sass.compiler_path._find_dart_sass_executable') as mock_find, \
             patch('importlib.import_module') as mock_import:
            
            # Mock platform module not found
            mock_import.side_effect = ImportError("No module named 'sass_embedded_linux_x64'")
            
            # Mock system Sass found
            mock_find.return_value = ['/usr/bin/sass']
            
            result = get_compiler_command()
            assert result == ['/usr/bin/sass']
    
    def test_get_compiler_command_no_compiler_found(self):
        """Test error when no compiler is found."""
        with patch.dict(os.environ, {}, clear=True), \
             patch('dart_sass.compiler_path._find_dart_sass_executable') as mock_find:
            
            # Mock no system Sass found
            mock_find.return_value = None
            
            # Mock platform module not found and sass package not available
            def mock_import_side_effect(module_name):
                if 'sass_embedded' in module_name or module_name == 'sass':
                    raise ImportError(f"No module named '{module_name}'")
                return MagicMock()
            
            with patch('importlib.import_module', side_effect=mock_import_side_effect):
                with pytest.raises(RuntimeError, match="Embedded Dart Sass couldn't find the embedded compiler executable"):
                    get_compiler_command()
