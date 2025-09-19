"""
Edge cases and error condition tests, based on Node.js reference implementation.
"""

import pytest
import tempfile
import os
from pathlib import Path
from dart_sass import compile, compile_string, compile_async, compile_string_async
from dart_sass.exception import CompileException
from dart_sass.importer_registry import ImporterResult
from dart_sass.canonicalize_context import CanonicalizeContext
from dart_sass.value.string import SassString
from dart_sass.value.number import SassNumber


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_string_compilation(self):
        """Test compiling empty string."""
        result = compile_string("")
        assert result['css'] == ""
    
    def test_whitespace_only_compilation(self):
        """Test compiling whitespace-only string."""
        result = compile_string("   \n  \t  \n  ")
        assert result['css'].strip() == ""
    
    def test_comment_only_compilation(self):
        """Test compiling comment-only string."""
        result = compile_string("/* This is a comment */")
        # Comments are preserved in expanded style (default)
        assert result['css'].strip() == "/* This is a comment */"
    
    def test_syntax_error_handling(self):
        """Test syntax error handling."""
        with pytest.raises(CompileException):
            compile_string(".test { color: ; }")  # Missing value
    
    def test_undefined_variable_error(self):
        """Test undefined variable error."""
        with pytest.raises(CompileException):
            compile_string(".test { color: $undefined-var; }")
    
    def test_invalid_function_call_error(self):
        """Test invalid syntax error (matches Node.js reference test)."""
        with pytest.raises(CompileException):
            compile_string("invalid")  # Invalid Sass syntax, not unknown function
    
    def test_circular_import_error(self):
        """Test circular import detection."""
        # Create two files that import each other
        with tempfile.TemporaryDirectory() as temp_dir:
            file1 = Path(temp_dir) / 'file1.scss'
            file2 = Path(temp_dir) / 'file2.scss'
            
            file1.write_text('@import "file2"; .file1 { color: red; }')
            file2.write_text('@import "file1"; .file2 { color: blue; }')
            
            with pytest.raises(CompileException):
                compile(str(file1), {'load_paths': [temp_dir]})
    
    def test_nonexistent_file_error(self):
        """Test error when compiling nonexistent file."""
        with pytest.raises(CompileException):
            compile("/nonexistent/file.scss")
    
    def test_nonexistent_import_error(self):
        """Test error when importing nonexistent file."""
        with pytest.raises(CompileException):
            compile_string('@import "nonexistent";')
    
    def test_invalid_sass_syntax(self):
        """Test invalid Sass syntax."""
        with pytest.raises(CompileException):
            compile_string(".test\n  color red")  # Missing colon and semicolon
    
    def test_unicode_content(self):
        """Test Unicode content handling."""
        scss_code = """
        .unicode-test {
            content: "Hello 世界 🌍";
            font-family: "Noto Sans CJK";
        }
        """
        
        result = compile_string(scss_code)
        css = result['css']
        
        assert "Hello 世界 🌍" in css
        assert "Noto Sans CJK" in css
    
    def test_very_long_content(self):
        """Test very long content compilation."""
        # Generate a large SCSS file
        rules = []
        for i in range(1000):
            rules.append(f".class-{i} {{ color: hsl({i % 360}, 50%, 50%); }}")
        
        scss_code = "\n".join(rules)
        result = compile_string(scss_code)
        
        assert len(result['css']) > 10000  # Should be substantial
        assert ".class-0" in result['css']
        assert ".class-999" in result['css']
    
    def test_deeply_nested_selectors(self):
        """Test deeply nested selectors."""
        scss_code = """
        .level1 {
            .level2 {
                .level3 {
                    .level4 {
                        .level5 {
                            color: red;
                        }
                    }
                }
            }
        }
        """
        
        result = compile_string(scss_code)
        css = result['css']
        
        assert ".level1 .level2 .level3 .level4 .level5" in css
    
    def test_custom_function_error_handling(self):
        """Test error handling in custom functions."""
        def error_function(args):
            raise ValueError("Custom function error")
        
        scss_code = ".test { color: error-func(); }"
        
        with pytest.raises(CompileException):
            compile_string(scss_code, {
                'functions': {
                    'error-func()': error_function
                }
            })
    
    def test_custom_function_invalid_return(self):
        """Test custom function with invalid return value."""
        def invalid_return_function(args):
            return "not a sass value"  # Should return SassValue
        
        scss_code = ".test { color: invalid-func(); }"
        
        with pytest.raises(CompileException):
            compile_string(scss_code, {
                'functions': {
                    'invalid-func()': invalid_return_function
                }
            })
    
    def test_importer_error_handling(self):
        """Test error handling in custom importers."""
        class ErrorImporter:
            def canonicalize(self, url, context):
                if url == 'error-import':
                    raise ValueError("Importer error")
                return None
            
            def load(self, canonical_url):
                return None
        
        scss_code = '@import "error-import";'
        
        with pytest.raises(CompileException):
            compile_string(scss_code, {
                'importers': [ErrorImporter()]
            })
    
    def test_importer_invalid_return(self):
        """Test importer with invalid return value."""
        class InvalidImporter:
            def canonicalize(self, url, context):
                if url == 'invalid':
                    return 123  # Should return string or None
                return None
            
            def load(self, canonical_url):
                return None
        
        scss_code = '@import "invalid";'
        
        with pytest.raises(CompileException):
            compile_string(scss_code, {
                'importers': [InvalidImporter()]
            })
    
    def test_file_importer_invalid_url(self):
        """Test file importer returning invalid URL."""
        class InvalidFileImporter:
            def find_file_url(self, url, context):
                if url == 'invalid':
                    return "not-a-file-url"  # Should return file: URL
                return None
        
        scss_code = '@import "invalid";'
        
        with pytest.raises(CompileException):
            compile_string(scss_code, {
                'importers': [InvalidFileImporter()]
            })
    
    def test_mixed_importer_types(self):
        """Test mixing regular and file importers."""
        class RegularImporter:
            def canonicalize(self, url, context):
                if url == 'regular':
                    return 'regular://test.scss'
                return None
            
            def load(self, canonical_url):
                if canonical_url == 'regular://test.scss':
                    return ImporterResult(contents='$color: blue;', syntax='scss')
                return None
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scss', delete=False) as f:
            f.write('$size: 10px;')
            temp_path = f.name
        
        class FileImporter:
            def find_file_url(self, url, context):
                if url == 'file-import':
                    return f'file://{temp_path}'
                return None
        
        try:
            scss_code = '''
            @import "regular";
            @import "file-import";
            .test {
                color: $color;
                font-size: $size;
            }
            '''
            
            result = compile_string(scss_code, {
                'importers': [RegularImporter(), FileImporter()]
            })
            
            css = result['css']
            assert 'color: blue' in css
            assert 'font-size: 10px' in css
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_async_error_handling(self):
        """Test error handling in async compilation."""
        with pytest.raises(CompileException):
            await compile_string_async(".test { color: ; }")
    
    @pytest.mark.asyncio
    async def test_async_file_error(self):
        """Test async file compilation error."""
        with pytest.raises(CompileException):
            await compile_async("/nonexistent/file.scss")
    
    def test_load_paths_with_nonexistent_directory(self):
        """Test load paths with nonexistent directory."""
        # Should not error, just not find imports
        scss_code = '@import "test";'
        
        with pytest.raises(CompileException):  # Import not found
            compile_string(scss_code, {
                'load_paths': ['/nonexistent/directory']
            })
    
    def test_empty_load_paths(self):
        """Test empty load paths."""
        scss_code = '@import "test";'
        
        with pytest.raises(CompileException):  # Import not found
            compile_string(scss_code, {
                'load_paths': []
            })
    
    def test_relative_import_resolution(self):
        """Test relative import resolution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested directory structure
            subdir = Path(temp_dir) / 'subdir'
            subdir.mkdir()
            
            # Create files
            main_file = Path(temp_dir) / 'main.scss'
            sub_file = subdir / 'sub.scss'
            
            sub_file.write_text('$color: green;')
            main_file.write_text('@import "subdir/sub"; .test { color: $color; }')
            
            result = compile(str(main_file))
            css = result['css']
            
            assert 'color: green' in css
    
    def test_partial_file_import(self):
        """Test importing partial files (underscore prefix)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create partial file
            partial_file = Path(temp_dir) / '_partial.scss'
            main_file = Path(temp_dir) / 'main.scss'
            
            partial_file.write_text('$partial-color: purple;')
            main_file.write_text('@import "partial"; .test { color: $partial-color; }')
            
            result = compile(str(main_file))
            css = result['css']
            
            assert 'color: purple' in css
