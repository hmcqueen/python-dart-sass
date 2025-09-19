# Contributing to Python Dart Sass

Thank you for your interest in contributing to Python Dart Sass! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Git
- **Dart Sass executable** (see installation options below)

#### Installing Dart Sass

You need Dart Sass installed for the tests to run. Choose one of these options:

**Option 1: Standalone (Recommended)**
```bash
# Download and install standalone Dart Sass
wget https://github.com/sass/dart-sass/releases/download/1.81.0/dart-sass-1.81.0-linux-x64.tar.gz
tar -xzf dart-sass-1.81.0-linux-x64.tar.gz
sudo mv dart-sass /usr/local/bin/
```

**Option 2: Package Manager**
```bash
# Homebrew
brew install sass/sass/sass

# npm
npm install -g sass
```

**Option 3: Custom Path**
```bash
# Set environment variable to point to your Dart Sass installation
export SASS_EMBEDDED_COMPILER_PATH="/path/to/dart-sass/executable"
```

### Getting Started

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/hmcqueen/python-dart-sass.git
   cd python-dart-sass
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Run tests to ensure everything works**
   ```bash
   uv run pytest
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=dart_sass

# Run specific test categories
uv run pytest tests/test_values.py      # Value type tests
uv run pytest tests/test_compiler.py    # Compiler tests
uv run pytest tests/test_protocol.py    # Protocol tests
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code
uv run black .
uv run isort .

# Check formatting
uv run black --check .
uv run isort --check-only .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src/dart_sass
```

## Project Structure

```
python-dart-sass/
├── src/
│   └── dart_sass/
│       ├── __init__.py              # Main API exports
│       ├── compiler/
│       │   ├── async_compiler.py    # Asynchronous compiler
│       │   ├── sync_compiler.py     # Synchronous compiler
│       │   └── utils.py             # Compiler utilities
│       ├── protocol/
│       │   ├── message_transformer.py  # Protocol message handling
│       │   ├── request_tracker.py      # Request/response tracking
│       │   └── dispatcher.py           # Message dispatching
│       ├── value/
│       │   ├── sass_boolean.py      # Sass boolean values
│       │   ├── sass_color.py        # Sass color values
│       │   ├── sass_list.py         # Sass list values
│       │   ├── sass_map.py          # Sass map values
│       │   ├── sass_null.py         # Sass null value
│       │   ├── sass_number.py       # Sass number values
│       │   └── sass_string.py       # Sass string values
│       ├── importer/
│       │   ├── file_importer.py     # File-based importers
│       │   └── importer.py          # Base importer classes
│       ├── function_registry.py     # Function registration system
│       ├── importer_registry.py     # Importer registration system
│       ├── value_converter.py       # Python ↔ Protobuf conversion
│       └── exception.py             # Exception classes
├── tests/
│   ├── test_values.py               # Value type tests
│   ├── test_compiler.py             # Compiler tests
│   ├── test_protocol.py             # Protocol tests
│   └── conftest.py                  # Test configuration
├── proto/                           # Protocol buffer definitions
├── pyproject.toml                   # Project configuration
└── README.md                        # Project documentation
```

## Architecture Overview

### Core Components

1. **Embedded Protocol Implementation**: Full implementation of the Sass Embedded Protocol
2. **Value System**: Complete Python representations of all Sass value types
3. **Compiler Management**: Async and sync compilers with subprocess lifecycle management
4. **Function Registry**: System for registering custom Python functions callable from Sass
5. **Importer Registry**: System for custom import logic and file resolution

### Key Design Principles

- **Protocol Compliance**: Follows the embedded host implementation patterns
- **Type Safety**: Comprehensive type hints and runtime type checking
- **Error Handling**: Detailed error reporting with source location information
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Contributing Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all public APIs
- Keep line length to 88 characters (Black default)
- Use descriptive variable and function names

### Testing

- Write tests for all new functionality
- Maintain high test coverage (aim for 90%+)
- Include both unit tests and integration tests
- Test cross-platform compatibility when relevant

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs with examples
- Include type information in docstrings
- Document any breaking changes in detail

### Commit Messages

Use clear, descriptive commit messages following conventional commits:

```
feat: add support for custom Sass functions

- Implement function registry with decorator support
- Add bidirectional value conversion system
- Include comprehensive tests for all value types
- Update documentation with usage examples

Closes #123
```

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- Python version and platform
- Dart Sass version
- Minimal code example that reproduces the issue
- Full error traceback
- Expected vs actual behavior

### Feature Requests

For new features, please:

- Describe the use case and motivation
- Check if the feature exists in the Node.js implementation
- Provide examples of how the feature would be used
- Consider performance implications

### Code Contributions

1. **Create an issue** first to discuss the change
2. **Fork the repository** and create a feature branch
3. **Implement the change** with comprehensive tests
4. **Ensure all tests pass** and code quality checks pass
5. **Update documentation** as needed
6. **Submit a pull request** with a clear description

## Protocol Implementation

### Embedded Sass Protocol

This project implements the [Embedded Sass Protocol](https://github.com/sass/sass/blob/main/spec/embedded-protocol.md). When making changes:

- Ensure compatibility with the protocol specification
- Test against the official Dart Sass embedded compiler
- Follow the Node.js reference implementation patterns
- Document any protocol-specific behavior

### Message Handling

- Use protocol buffers for all communication
- Implement proper message framing with varint length prefixes
- Handle streaming and partial messages correctly
- Provide comprehensive error handling

### Value Conversion

- Maintain bidirectional conversion between Python and Sass values
- Ensure type safety and proper validation
- Handle edge cases and error conditions
- Test all value type combinations

## Getting Help

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and implementation discussion
- **Protocol Questions**: Refer to the official Embedded Sass Protocol specification

## License

By contributing to Python Dart Sass, you agree that your contributions will be licensed under the MIT License.
