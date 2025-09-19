"""
Comprehensive tests for all compile options, based on Node.js reference implementation.
"""

import pytest
import tempfile
import os
from pathlib import Path
from dart_sass import compile, compile_string, compile_async, compile_string_async
from dart_sass.exception import CompileException


class TestCompileOptions:
    """Test all compile options comprehensively."""
    
    def test_style_expanded(self):
        """Test expanded output style (default)."""
        scss_code = """
        .test {
            color: red;
            background: blue;
        }
        """
        
        result = compile_string(scss_code, {'style': 'expanded'})
        css = result['css']
        
        # Expanded style should have newlines and indentation
        assert '.test {' in css
        assert '  color: red;' in css
        assert '  background: blue;' in css
        assert '}' in css
    
    def test_style_compressed(self):
        """Test compressed output style."""
        scss_code = """
        .test {
            color: red;
            background: blue;
        }
        """
        
        result = compile_string(scss_code, {'style': 'compressed'})
        css = result['css']
        
        # Compressed style should be minified
        assert '.test{color:red;background:blue}' in css.replace(' ', '').replace('\n', '')
    
    def test_source_map_true(self):
        """Test source map generation."""
        scss_code = ".test { color: red; }"
        
        result = compile_string(scss_code, {'source_map': True})
        
        assert 'source_map' in result
        assert result['source_map'] is not None
        # Source map should be a dict/object (like Node.js RawSourceMap), not a string
        assert isinstance(result['source_map'], dict)
        assert 'version' in result['source_map']
    
    def test_source_map_false(self):
        """Test no source map generation."""
        scss_code = ".test { color: red; }"
        
        result = compile_string(scss_code, {'source_map': False})
        
        assert result['source_map'] is None
    
    def test_source_map_include_sources(self):
        """Test source map with included sources."""
        scss_code = ".test { color: red; }"
        
        result = compile_string(scss_code, {
            'source_map': True,
            'source_map_include_sources': True
        })
        
        assert result['source_map'] is not None
        # Should include the original source in the source map
        assert 'sourcesContent' in result['source_map']
    
    def test_charset_true(self):
        """Test charset option enabled."""
        scss_code = ".test { content: 'café'; }"
        
        result = compile_string(scss_code, {'charset': True})
        css = result['css']
        
        # Should include @charset if non-ASCII characters are present
        # Note: This depends on the actual Sass compiler behavior
        assert 'café' in css
    
    def test_charset_false(self):
        """Test charset option disabled."""
        scss_code = ".test { content: 'café'; }"
        
        result = compile_string(scss_code, {'charset': False})
        css = result['css']
        
        # Should not include @charset even with non-ASCII characters
        assert 'café' in css
        assert '@charset' not in css
    
    def test_verbose_option(self):
        """Test verbose logging option."""
        scss_code = ".test { color: red; }"
        
        # This mainly affects logging, hard to test output directly
        result = compile_string(scss_code, {'verbose': True})
        assert result['css'] is not None
    
    def test_quiet_deps_option(self):
        """Test quiet dependencies option."""
        scss_code = ".test { color: red; }"
        
        result = compile_string(scss_code, {'quiet_deps': True})
        assert result['css'] is not None
    
    def test_silent_option(self):
        """Test silent option."""
        scss_code = ".test { color: red; }"
        
        result = compile_string(scss_code, {'silent': True})
        assert result['css'] is not None
    
    def test_alert_color_option(self):
        """Test alert color option."""
        scss_code = ".test { color: red; }"
        
        result = compile_string(scss_code, {'alert_color': True})
        assert result['css'] is not None
    
    def test_alert_ascii_option(self):
        """Test alert ASCII option."""
        scss_code = ".test { color: red; }"
        
        result = compile_string(scss_code, {'alert_ascii': True})
        assert result['css'] is not None
    
    def test_multiple_options_combined(self):
        """Test multiple options combined."""
        scss_code = """
        .test {
            color: red;
            background: blue;
        }
        """
        
        result = compile_string(scss_code, {
            'style': 'compressed',
            'source_map': True,
            'charset': False,
            'verbose': False,
            'quiet_deps': True
        })
        
        css = result['css']
        
        # Should be compressed
        assert len(css.split('\n')) <= 2  # Compressed should be few lines
        
        # Should have source map
        assert result['source_map'] is not None
    
    @pytest.mark.asyncio
    async def test_async_compile_with_options(self):
        """Test async compilation with options."""
        scss_code = """
        .async-test {
            color: green;
            font-size: 16px;
        }
        """
        
        result = await compile_string_async(scss_code, {
            'style': 'compressed',
            'source_map': True
        })
        
        css = result['css']
        
        # Should be compressed
        assert '.async-test{' in css.replace(' ', '')
        
        # Should have source map
        assert result['source_map'] is not None
    
    def test_file_compile_with_options(self):
        """Test file compilation with options."""
        scss_content = """
        .file-test {
            color: purple;
            margin: 10px;
        }
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scss', delete=False) as f:
            f.write(scss_content)
            temp_path = f.name
        
        try:
            result = compile(temp_path, {
                'style': 'expanded',
                'source_map': True
            })
            
            css = result['css']
            
            # Should be expanded
            assert '.file-test {' in css
            assert '  color: purple;' in css
            
            # Should have source map
            assert result['source_map'] is not None
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_async_file_compile_with_options(self):
        """Test async file compilation with options."""
        scss_content = """
        .async-file-test {
            color: orange;
            padding: 5px;
        }
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scss', delete=False) as f:
            f.write(scss_content)
            temp_path = f.name
        
        try:
            result = await compile_async(temp_path, {
                'style': 'compressed',
                'source_map': False
            })
            
            css = result['css']
            
            # Should be compressed
            assert '.async-file-test{' in css.replace(' ', '')
            
            # Should not have source map
            assert result['source_map'] is None
            
        finally:
            os.unlink(temp_path)
    
    def test_invalid_style_option(self):
        """Test invalid style option throws error (Node.js behavior)."""
        scss_code = ".test { color: red; }"
        
        # Invalid style should throw error (like Node.js: throw new Error(`Unknown options.style: "${options?.style}"`))
        with pytest.raises(ValueError, match='Unknown options.style: "invalid"'):
            compile_string(scss_code, {'style': 'invalid'})
    
    def test_deprecation_options(self):
        """Test deprecation handling options."""
        scss_code = ".test { color: red; }"
        
        # These options control deprecation warnings
        result = compile_string(scss_code, {
            'fatal_deprecation': [],
            'silence_deprecation': [],
            'future_deprecation': []
        })
        
        assert result['css'] is not None
    
    def test_string_deprecation_options(self):
        """Test deprecation options with string values."""
        scss_code = ".test { color: red; }"
        
        # Test single string values
        result = compile_string(scss_code, {
            'fatal_deprecation': 'some-deprecation',
            'silence_deprecation': 'other-deprecation'
        })
        
        assert result['css'] is not None
