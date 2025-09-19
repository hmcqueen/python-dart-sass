# Python Dart Sass

A Python implementation of the Embedded Sass Host, providing a Python API for the Dart Sass compiler using the embedded protocol.

## Features

- 🚀 **Modern Architecture** - Uses Dart Sass embedded protocol for compilation
- 🔄 **Async Support** - Both synchronous and asynchronous APIs
- 🎯 **Custom Functions** - Register Python functions callable from Sass
- 📁 **Custom Importers** - Handle custom import logic in Python
- 🛠️ **Full Sass Support** - Complete Sass language feature support via Dart Sass
- 🧪 **Well Tested** - Comprehensive test suite with 278 passing tests

## Installation

### Prerequisites

This package requires the Dart Sass compiler to be installed on your system. You have several options:

#### Option 1: Standalone Dart Sass (Recommended)

Download the standalone Dart Sass binary from the [official releases](https://github.com/sass/dart-sass/releases):

```bash
# Linux x64
wget https://github.com/sass/dart-sass/releases/download/1.81.0/dart-sass-1.81.0-linux-x64.tar.gz
tar -xzf dart-sass-1.81.0-linux-x64.tar.gz
sudo mv dart-sass /usr/local/bin/

# macOS x64
wget https://github.com/sass/dart-sass/releases/download/1.81.0/dart-sass-1.81.0-macos-x64.tar.gz
tar -xzf dart-sass-1.81.0-macos-x64.tar.gz
sudo mv dart-sass /usr/local/bin/

# Windows x64
# Download dart-sass-1.81.0-windows-x64.zip and extract to your PATH
```

#### Option 2: Using Package Managers

```bash
# Homebrew (macOS/Linux)
brew install sass/sass/sass

# Chocolatey (Windows)
choco install sass

# npm (if you have Node.js)
npm install -g sass
```

#### Option 3: Custom Installation Path

If you install Dart Sass to a custom location, set the environment variable:

```bash
export SASS_EMBEDDED_COMPILER_PATH="/path/to/your/sass"
```

### Installing Python Dart Sass

**Note**: This package is not yet published to PyPI. To use it, you'll need to install from source or wait for the official release.

```bash
# Install from source (when available)
pip install git+https://github.com/hmcqueen/python-dart-sass.git

# Or install locally for development
pip install -e .

# When published to PyPI (future):
pip install python-dart-sass
```

## Quick Start

### Basic Usage

```python
import dart_sass as sass

# Compile from string
result = sass.compile_string("""
$primary: #007bff;
.button {
    background-color: $primary;
    padding: 0.5rem 1rem;
}
""")
print(result.css)

# Compile from file
result = sass.compile('styles.scss')
print(result.css)
```

### Async Usage

```python
import dart_sass as sass
import asyncio

async def compile_sass():
    result = await sass.compile_async('styles.scss')
    print(result.css)

asyncio.run(compile_sass())
```

## Advanced Features

### Custom Functions

Register Python functions that can be called from Sass:

```python
import dart_sass as sass
from dart_sass.value import SassString, SassNumber

def pow_function(args):
    """Calculate power: pow($base, $exponent)"""
    base = args[0].assert_number().value
    exponent = args[1].assert_number().value
    return SassNumber(base ** exponent)

# Compile with custom function
result = sass.compile_string("""
.element {
    width: pow(2, 3) * 1px; // Results in 8px
}
""", functions={
    'pow($base, $exponent)': pow_function
})
```

### Custom Importers

Handle custom import logic:

```python
import dart_sass as sass
from dart_sass.importer import Importer, ImportResult

class ThemeImporter(Importer):
    def canonicalize(self, url, context):
        if url.startswith('theme:'):
            return f'file:///themes/{url[6:]}.scss'
        return None
    
    def load(self, canonical_url):
        # Load theme file content
        theme_name = canonical_url.split('/')[-1].replace('.scss', '')
        content = f"$theme: '{theme_name}';"
        return ImportResult(content, syntax='scss')

result = sass.compile_string("""
@import 'theme:dark';
.app { color: $theme; }
""", importers=[ThemeImporter()])
```

### File Importers

For simpler file-based imports:

```python
from dart_sass.importer import FileImporter

class NodeModulesImporter(FileImporter):
    def find_file_url(self, url, context):
        if not url.startswith('~'):
            return None
        
        # Handle npm-style imports: @import '~bootstrap/scss/bootstrap'
        package_path = url[1:]  # Remove ~
        file_path = f'node_modules/{package_path}'
        
        if os.path.exists(f'{file_path}.scss'):
            return f'file://{os.path.abspath(file_path)}.scss'
        return None

result = sass.compile_string("""
@import '~bootstrap/scss/variables';
""", importers=[NodeModulesImporter()])
```

## Sass Value Types

The package provides Python representations of all Sass value types:

```python
from dart_sass.value import *

# Numbers
num = SassNumber(42, unit='px')
print(num.value)  # 42
print(num.unit)   # 'px'

# Strings
string = SassString('hello world', quoted=True)
print(string.text)    # 'hello world'
print(string.quoted)  # True

# Colors
color = SassColor.rgb(255, 0, 0)  # Red
print(color.red)    # 255
print(color.green)  # 0
print(color.blue)   # 0

# Lists
sass_list = SassList([
    SassNumber(1),
    SassNumber(2),
    SassNumber(3)
], separator=',')

# Maps
sass_map = SassMap({
    SassString('primary'): SassColor.rgb(0, 123, 255),
    SassString('secondary'): SassColor.rgb(108, 117, 125)
})

# Booleans and null
sass_true = SassBoolean.sass_true
sass_false = SassBoolean.sass_false
sass_null = SassNull.sass_null
```

## Compilation Options

```python
result = sass.compile_string(scss_content, {
    # Output style
    'style': 'compressed',  # 'expanded', 'compressed'
    
    # Source maps
    'source_map': True,
    
    # Load paths for @import
    'load_paths': ['/path/to/sass', '/another/path'],
    
    # Custom functions
    'functions': {
        'custom-function($arg)': my_function
    },
    
    # Custom importers
    'importers': [MyImporter()],
    
    # Charset handling
    'charset': True,
    
    # Quiet dependency warnings
    'quiet_deps': True,
    
    # Verbose output
    'verbose': False
})

print(result.css)
print(result.source_map)  # If source_map=True
print(result.loaded_urls)  # List of imported file URLs
```

## Error Handling

```python
from dart_sass.exception import CompileException

try:
    result = sass.compile_string("""
    .invalid {
        color: $undefined-variable;
    }
    """)
except CompileException as e:
    print(f"Compilation failed: {e}")
    # Exception includes detailed error information with line numbers
```

## Performance Considerations

### Async vs Sync

The asynchronous API may be beneficial for multiple compilations since it runs Dart Sass in a separate process:

```python
import asyncio
import dart_sass as sass

async def compile_multiple():
    tasks = [
        sass.compile_async('file1.scss'),
        sass.compile_async('file2.scss'),
        sass.compile_async('file3.scss')
    ]
    results = await asyncio.gather(*tasks)
    return results

# This allows concurrent compilation vs sequential sync API
results = asyncio.run(compile_multiple())
```

### Compiler Lifecycle

For multiple compilations, you can manage the compiler lifecycle to avoid repeated initialization:

```python
# Initialize once, use multiple times
compiler = sass.init_async_compiler()

try:
    result1 = await compiler.compile_string(scss1)
    result2 = await compiler.compile_string(scss2)
    result3 = await compiler.compile_string(scss3)
finally:
    await compiler.dispose()  # Clean up resources
```

## Architecture

This package implements the [Embedded Sass Protocol](https://github.com/sass/sass/blob/main/spec/embedded-protocol.md) to communicate with Dart Sass:

1. **Protocol Communication**: Uses protocol buffers over stdin/stdout
2. **Message Handling**: Reactive streams for handling compilation requests/responses
3. **Value Conversion**: Bidirectional conversion between Python and Sass value types
4. **Process Management**: Manages Dart Sass subprocess lifecycle
5. **Cross-Platform**: Works on Linux, macOS, and Windows

### Key Components

- **Compilers**: `AsyncCompiler` and `SyncCompiler` for different usage patterns
- **Value System**: Complete Sass value type implementations
- **Protocol Layer**: Message encoding/decoding and transport
- **Importers**: File and custom importer interfaces
- **Functions**: Custom function registration and calling

## Development

This project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=sass_embedded

# Linting and formatting
uv run ruff check
uv run black --check .
uv run isort --check-only .

# Format code
uv run black .
uv run isort .
```

### Testing

The test suite includes:
- Unit tests for all value types
- Integration tests with real Sass compilation
- Protocol communication tests
- Cross-platform compatibility tests

```bash
# Run specific test categories
uv run pytest tests/test_values.py      # Value type tests
uv run pytest tests/test_compiler.py    # Compiler tests
uv run pytest tests/test_protocol.py    # Protocol tests
```

## Compatibility

- **Python**: 3.10+
- **Dart Sass**: 1.45.0+ (embedded protocol support)
- **Platforms**: Linux, macOS, Windows
- **Architecture**: x86_64, ARM64

## Comparison with Other Sass Packages

| Feature | python-dart-sass | libsass-python | pysass |
|---------|---------------|----------------|--------|
| Sass Version | Latest Dart Sass | LibSass (deprecated) | LibSass |
| Architecture | Separate process | Native extension | Native extension |
| Async Support | ✅ | ❌ | ❌ |
| Custom Functions | ✅ | ✅ | ✅ |
| Custom Importers | ✅ | ✅ | Limited |
| Source Maps | ✅ | ✅ | ✅ |
| Active Development | ✅ | ❌ | ❌ |

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`uv run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Acknowledgments

This Python implementation was developed by Harvey McQueen with assistance from Amazon Q Command-line. It is:

- Based on the [Embedded Sass Protocol](https://github.com/sass/sass/blob/main/spec/embedded-protocol.md)
- Inspired by the [Node.js Embedded Sass Host](https://github.com/sass/embedded-host-node)
- Uses [Dart Sass](https://sass-lang.com/dart-sass) as the compilation engine

This is an independent Python implementation and is not affiliated with or endorsed by the official Sass team.
