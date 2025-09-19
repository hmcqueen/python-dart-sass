"""
Comprehensive tests for async compiler functionality.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from dart_sass import compile_async, compile_string_async, AsyncCompiler, init_async_compiler
from dart_sass.exception import CompileException
from dart_sass.importer_registry import ImporterResult
from dart_sass.value.string import SassString
from dart_sass.value.number import SassNumber


class TestAsyncCompiler:
    """Test async compiler functionality comprehensively."""
    
    @pytest.mark.asyncio
    async def test_basic_async_compilation(self):
        """Test basic async string compilation."""
        scss_code = """
        .async-basic {
            color: red;
            font-size: 14px;
        }
        """
        
        result = await compile_string_async(scss_code)
        css = result['css']
        
        assert '.async-basic' in css
        assert 'color: red' in css
        assert 'font-size: 14px' in css
    
    @pytest.mark.asyncio
    async def test_async_file_compilation(self):
        """Test async file compilation."""
        scss_content = """
        .async-file {
            background: blue;
            margin: 20px;
        }
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scss', delete=False) as f:
            f.write(scss_content)
            temp_path = f.name
        
        try:
            result = await compile_async(temp_path)
            css = result['css']
            
            assert '.async-file' in css
            assert 'background: blue' in css
            assert 'margin: 20px' in css
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_async_with_options(self):
        """Test async compilation with various options."""
        scss_code = """
        .async-options {
            color: green;
            padding: 10px;
        }
        """
        
        result = await compile_string_async(scss_code, {
            'style': 'compressed',
            'source_map': True,
            'charset': False
        })
        
        css = result['css']
        
        # Should be compressed
        assert '.async-options{' in css.replace(' ', '')
        
        # Should have source map
        assert result['source_map'] is not None
    
    @pytest.mark.asyncio
    async def test_async_custom_functions(self):
        """Test async compilation with custom functions."""
        def multiply_function(args):
            num1 = args[0].assert_number()
            num2 = args[1].assert_number()
            return SassNumber(num1.value * num2.value, num1.unit)
        
        scss_code = """
        .async-function {
            width: multiply(10px, 2);
            height: multiply(5em, 3);
        }
        """
        
        result = await compile_string_async(scss_code, {
            'functions': {
                'multiply($a, $b)': multiply_function
            }
        })
        
        css = result['css']
        assert 'width: 20px' in css
        assert 'height: 15em' in css
    
    @pytest.mark.asyncio
    async def test_async_custom_importers(self):
        """Test async compilation with custom importers."""
        class AsyncTestImporter:
            def canonicalize(self, url, context):
                if url == 'async-import':
                    return 'async://test.scss'
                return None
            
            def load(self, canonical_url):
                if canonical_url == 'async://test.scss':
                    return ImporterResult(
                        contents='$async-color: orange;',
                        syntax='scss'
                    )
                return None
        
        scss_code = """
        @import "async-import";
        .async-importer {
            color: $async-color;
        }
        """
        
        result = await compile_string_async(scss_code, {
            'importers': [AsyncTestImporter()]
        })
        
        css = result['css']
        assert 'color: orange' in css
    
    @pytest.mark.asyncio
    async def test_async_file_importers(self):
        """Test async compilation with file importers."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scss', delete=False) as f:
            f.write('$file-color: cyan;')
            temp_path = f.name
        
        class AsyncFileImporter:
            def find_file_url(self, url, context):
                if url == 'async-file':
                    return f'file://{temp_path}'
                return None
        
        try:
            scss_code = """
            @import "async-file";
            .async-file-importer {
                color: $file-color;
            }
            """
            
            result = await compile_string_async(scss_code, {
                'importers': [AsyncFileImporter()]
            })
            
            css = result['css']
            assert 'color: cyan' in css
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_async_error_handling(self):
        """Test async error handling."""
        with pytest.raises(CompileException):
            await compile_string_async(".test { color: ; }")
    
    @pytest.mark.asyncio
    async def test_async_file_not_found(self):
        """Test async file not found error."""
        with pytest.raises(CompileException):
            await compile_async("/nonexistent/async-file.scss")
    
    @pytest.mark.asyncio
    async def test_multiple_async_compilations(self):
        """Test multiple async compilations running concurrently."""
        scss_codes = [
            ".test1 { color: red; }",
            ".test2 { color: blue; }",
            ".test3 { color: green; }",
            ".test4 { color: yellow; }",
            ".test5 { color: purple; }"
        ]
        
        # Run all compilations concurrently
        tasks = [compile_string_async(code) for code in scss_codes]
        results = await asyncio.gather(*tasks)
        
        # Check all results
        for i, result in enumerate(results):
            css = result['css']
            assert f'.test{i+1}' in css
    
    @pytest.mark.asyncio
    async def test_async_compiler_lifecycle(self):
        """Test async compiler initialization and disposal."""
        compiler = await init_async_compiler()
        
        try:
            # Test compilation
            result = await compiler.compile_string_async(".test { color: red; }")
            assert '.test' in result['css']
            
            # Test file compilation
            with tempfile.NamedTemporaryFile(mode='w', suffix='.scss', delete=False) as f:
                f.write('.file-test { color: blue; }')
                temp_path = f.name
            
            try:
                result = await compiler.compile_async(temp_path)
                assert '.file-test' in result['css']
            finally:
                os.unlink(temp_path)
                
        finally:
            await compiler.dispose()
    
    @pytest.mark.asyncio
    async def test_async_compiler_reuse(self):
        """Test reusing async compiler for multiple compilations."""
        compiler = await init_async_compiler()
        
        try:
            # Multiple compilations with same compiler
            result1 = await compiler.compile_string_async(".test1 { color: red; }")
            result2 = await compiler.compile_string_async(".test2 { color: blue; }")
            result3 = await compiler.compile_string_async(".test3 { color: green; }")
            
            assert '.test1' in result1['css']
            assert '.test2' in result2['css']
            assert '.test3' in result3['css']
            
        finally:
            await compiler.dispose()
    
    @pytest.mark.asyncio
    async def test_async_compiler_with_options(self):
        """Test async compiler with options."""
        compiler = await init_async_compiler()
        
        try:
            scss_code = """
            .compiler-options {
                color: red;
                background: blue;
            }
            """
            
            result = await compiler.compile_string_async(scss_code, {
                'style': 'compressed',
                'source_map': True
            })
            
            css = result['css']
            
            # Should be compressed
            assert '.compiler-options{' in css.replace(' ', '')
            
            # Should have source map
            assert result['source_map'] is not None
            
        finally:
            await compiler.dispose()
    
    @pytest.mark.asyncio
    async def test_async_compiler_disposed_error(self):
        """Test error when using disposed async compiler."""
        compiler = await init_async_compiler()
        await compiler.dispose()
        
        # Should raise error when using disposed compiler
        with pytest.raises(CompileException):
            await compiler.compile_string_async(".test { color: red; }")
    
    @pytest.mark.asyncio
    async def test_async_with_load_paths(self):
        """Test async compilation with load paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create imported file
            imported_file = Path(temp_dir) / '_variables.scss'
            imported_file.write_text('$primary: magenta;')
            
            # Create main file
            main_file = Path(temp_dir) / 'main.scss'
            main_file.write_text('@import "variables"; .test { color: $primary; }')
            
            result = await compile_async(str(main_file), {
                'load_paths': [str(temp_dir)]
            })
            
            css = result['css']
            assert 'color: magenta' in css
    
    @pytest.mark.asyncio
    async def test_async_unicode_handling(self):
        """Test async compilation with Unicode content."""
        scss_code = """
        .unicode-async {
            content: "Hello 世界 🚀";
            font-family: "Noto Sans";
        }
        """
        
        result = await compile_string_async(scss_code)
        css = result['css']
        
        assert "Hello 世界 🚀" in css
        assert "Noto Sans" in css
    
    @pytest.mark.asyncio
    async def test_async_large_compilation(self):
        """Test async compilation with large content."""
        # Generate large SCSS content
        rules = []
        for i in range(500):
            rules.append(f".async-class-{i} {{ color: hsl({i % 360}, 50%, 50%); }}")
        
        scss_code = "\n".join(rules)
        result = await compile_string_async(scss_code)
        
        css = result['css']
        assert len(css) > 5000
        assert ".async-class-0" in css
        assert ".async-class-499" in css
    
    @pytest.mark.asyncio
    async def test_async_timeout_handling(self):
        """Test async compilation doesn't hang indefinitely."""
        # This test ensures async operations complete in reasonable time
        scss_code = ".timeout-test { color: red; }"
        
        # Should complete within 10 seconds
        result = await asyncio.wait_for(
            compile_string_async(scss_code),
            timeout=10.0
        )
        
        assert '.timeout-test' in result['css']
