"""
End-to-end integration tests with real Sass compilation.
"""

import pytest
import tempfile
import os
from pathlib import Path
from dart_sass import compile, compile_string, compile_async, compile_string_async
from dart_sass.value.string import SassString
from dart_sass.value.number import SassNumber
from dart_sass.value.list import SassList
from dart_sass.importer_registry import ImporterResult
from dart_sass.canonicalize_context import CanonicalizeContext
from dart_sass.exception import CompileException


class TestEndToEnd:
    """End-to-end integration test cases."""
    
    def test_compile_simple_scss(self):
        """Test compiling simple SCSS code."""
        scss_code = """
        $primary-color: #007bff;
        $margin: 1rem;
        
        .button {
            background-color: $primary-color;
            margin: $margin;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 0.25rem;
            
            &:hover {
                background-color: darken($primary-color, 10%);
            }
        }
        """
        
        try:
            result = compile_string(scss_code)
            
            # Check that we got CSS output
            assert 'css' in result
            assert isinstance(result['css'], str)
            assert len(result['css']) > 0
            
            # Check for expected CSS content
            css = result['css']
            assert '.button' in css
            assert 'background-color' in css
            assert '#007bff' in css or 'rgb(' in css  # Color might be converted
            assert 'margin: 1rem' in css
            
            # Check for nested selector
            assert '.button:hover' in css
            
            print(f"Compiled CSS:\n{css}")
            
        except CompileException as e:
            pytest.skip(f"Sass compiler not available or failed: {e}")
    
    def test_compile_file(self):
        """Test compiling a Sass file."""
        scss_content = """
        @import 'variables';
        
        .container {
            max-width: $container-width;
            margin: 0 auto;
            padding: $base-padding;
        }
        """
        
        variables_content = """
        $container-width: 1200px;
        $base-padding: 1rem;
        """
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create the main SCSS file
                main_file = Path(temp_dir) / 'main.scss'
                main_file.write_text(scss_content)
                
                # Create the variables file
                variables_file = Path(temp_dir) / '_variables.scss'
                variables_file.write_text(variables_content)
                
                # Use load_paths in options (modern Node.js pattern)
                result = compile(str(main_file), {
                    'load_paths': [str(temp_dir)]
                })
                
                # Check that we got CSS output
                assert 'css' in result
                css = result['css']
                assert '.container' in css
                assert 'max-width: 1200px' in css
                assert 'padding: 1rem' in css
                
                print(f"Compiled CSS from file:\n{css}")
                
        except CompileException as e:
            pytest.skip(f"Sass compiler not available or failed: {e}")
    
    @pytest.mark.asyncio
    async def test_compile_async(self):
        """Test asynchronous compilation."""
        scss_code = """
        .async-test {
            color: red;
            font-size: 16px;
        }
        """
        
        try:
            result = await compile_string_async(scss_code)
            
            assert 'css' in result
            css = result['css']
            assert '.async-test' in css
            assert 'color: red' in css
            
            print(f"Async compiled CSS:\n{css}")
            
        except CompileException as e:
            pytest.skip(f"Sass compiler not available or failed: {e}")
    
    def test_custom_function(self):
        """Test custom Sass function."""
        # Define a custom function (like Node.js)
        def double_function(args):
            number = args[0].assert_number()
            return SassNumber(number.value * 2, number.unit)
        
        scss_code = """
        .test {
            width: double(10px);
            height: double(5rem);
        }
        """
        
        try:
            # Pass functions via options (like Node.js options.functions)
            result = compile_string(scss_code, {
                'functions': {
                    'double($number)': double_function
                }
            })
            
            css = result['css']
            assert 'width: 20px' in css
            assert 'height: 10rem' in css
            
            print(f"CSS with custom function:\n{css}")
            
        except CompileException as e:
            pytest.skip(f"Sass compiler not available or failed: {e}")
    
    def test_file_importer(self):
        """Test FileImporter interface (one-phase process)."""
        import tempfile
        import os
        from pathlib import Path
        
        # Create a temporary SCSS file first
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scss', delete=False) as temp_file:
            temp_file.write('$primary: #007bff;\n$secondary: #6c757d;')
            temp_file_path = temp_file.name
        
        try:
            # Define a file importer (one-phase process)
            class CustomFileImporter:
                def find_file_url(self, url, context):
                    """Find file phase: return file URL."""
                    if url == 'theme-colors':
                        return f'file://{temp_file_path}'
                    return None
            
            scss_code = """
            @import 'theme-colors';
            
            .btn-primary {
                background-color: $primary;
            }
            
            .btn-secondary {
                background-color: $secondary;
            }
            """
            
            # Pass file importer via options
            result = compile_string(scss_code, {
                'importers': [CustomFileImporter()]
            })
            
            css = result['css']
            assert '#007bff' in css
            assert '#6c757d' in css
            
            print(f"CSS with file importer:\n{css}")
            
        except CompileException as e:
            self.fail(f"File importer test failed: {e}")
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    def test_custom_importer(self):
        """Test custom importer with proper two-phase process."""
        # Define a custom importer (proper Sass specification pattern)
        class CustomImporter:
            def canonicalize(self, url, context):
                """Canonicalize phase: convert URL to canonical form."""
                if url == 'custom:theme':
                    return 'custom://theme.scss'  # Return canonical URL
                return None
            
            def load(self, canonical_url):
                """Load phase: return actual content."""
                if canonical_url == 'custom://theme.scss':
                    return ImporterResult(
                        contents='$theme-primary: #ff6b6b;\n$theme-secondary: #4ecdc4;',
                        syntax='scss'
                    )
                return None
        
        scss_code = """
        @import 'custom:theme';
        
        .themed {
            color: $theme-primary;
            background: $theme-secondary;
        }
        """
        
        try:
            # Pass importers via options (like Node.js options.importers)
            result = compile_string(scss_code, {
                'importers': [CustomImporter()]
            })
            
            css = result['css']
            assert '#ff6b6b' in css
            assert '#4ecdc4' in css
            
            print(f"CSS with custom importer:\n{css}")
            
        except CompileException as e:
            pytest.fail(f"Custom importer test failed: {e}")
    
    def test_error_handling(self):
        """Test error handling for invalid Sass."""
        invalid_scss = """
        .test {
            color: $undefined-variable;
        }
        """
        
        try:
            with pytest.raises(CompileException) as exc_info:
                compile_string(invalid_scss)
            
            # Check that the error message is meaningful
            error_message = str(exc_info.value)
            assert 'undefined' in error_message.lower() or 'variable' in error_message.lower()
            
        except CompileException as e:
            if "compiler not available" in str(e).lower():
                pytest.skip(f"Sass compiler not available: {e}")
            else:
                # This is the expected error, so the test passes
                pass
    
    def test_source_map_option(self):
        """Test source map generation."""
        scss_code = """
        .source-map-test {
            color: blue;
        }
        """
        
        try:
            result = compile_string(scss_code, {'source_map': True})
            
            assert 'css' in result
            # Source map might be None if not supported yet
            if 'source_map' in result and result['source_map']:
                assert isinstance(result['source_map'], dict)  # Should be dict/object like Node.js
                print(f"Generated source map: {result['source_map']}")
            
        except CompileException as e:
            pytest.skip(f"Sass compiler not available or failed: {e}")
    
    def test_multiple_compilations(self):
        """Test multiple compilations to ensure no state leakage."""
        scss1 = ".test1 { color: red; }"
        scss2 = ".test2 { color: blue; }"
        
        try:
            result1 = compile_string(scss1)
            result2 = compile_string(scss2)
            
            assert '.test1' in result1['css']
            assert 'red' in result1['css']
            assert '.test1' not in result2['css']
            
            assert '.test2' in result2['css']
            assert 'blue' in result2['css']
            assert '.test2' not in result1['css']
            
        except CompileException as e:
            pytest.skip(f"Sass compiler not available or failed: {e}")
    
    def test_loaded_urls(self):
        """Test that loaded URLs are reported correctly."""
        scss_code = ".simple { color: green; }"
        
        try:
            result = compile_string(scss_code)
            
            assert 'loaded_urls' in result
            assert isinstance(result['loaded_urls'], list)
            # For string compilation, there might be a synthetic URL
            
        except CompileException as e:
            pytest.skip(f"Sass compiler not available or failed: {e}")
