# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-XX

### Added

#### Core Features
- **Complete Embedded Sass Protocol implementation** following the official specification
- **Synchronous and asynchronous APIs** for different usage patterns
- **Custom function support** with Python function registration
- **Custom importer support** with file-based and custom import logic
- **Complete Sass value system** with Python representations of all Sass types

#### Value System
- **SassNumber** with unit support and arithmetic operations
- **SassString** with quoted/unquoted variants
- **SassColor** with RGB, HSL, HWB color space support and conversions
- **SassList** with comma/space separators and immutable operations
- **SassMap** with immutable key-value operations
- **SassBoolean** with singleton true/false values
- **SassNull** singleton value
- **SassFunction** for function references

#### Compiler System
- **AsyncCompiler** for high-performance non-blocking compilation
- **SyncCompiler** for traditional blocking compilation
- **Compiler lifecycle management** with proper resource cleanup
- **Cross-platform support** (Linux, macOS, Windows)
- **Dart Sass executable detection** with multiple fallback strategies

#### Protocol Implementation
- **Protocol buffer communication** with Dart Sass subprocess
- **Message framing** with varint length prefixes
- **Streaming message handling** with partial message support
- **Request/response tracking** with thread-safe operations
- **Error handling** with detailed compilation error reporting

#### Advanced Features
- **Function registry** with decorator-based registration
- **Importer registry** with file and custom importer support
- **Value conversion system** for bidirectional Python ↔ Sass value conversion
- **CLI interface** for command-line usage
- **Comprehensive error handling** with source location information

### Technical Details

#### Architecture
- **Reactive streams** using RxPY for message handling
- **Immutable data structures** for Sass values using immutables library
- **Type safety** with comprehensive type hints throughout
- **Protocol compliance** following Node.js reference implementation patterns
- **Performance optimization** with efficient subprocess communication

#### Dependencies
- **Python**: 3.10+
- **protobuf**: Protocol buffer support for Sass communication
- **reactivex**: Reactive streams for message handling
- **colorspacious**: Color space conversions for Sass colors
- **immutables**: Immutable data structures for Sass values
- **varint**: Variable-length integer encoding for message framing

#### Testing
- **Comprehensive test suite** with 125+ tests
- **100% pass rate** across all test categories
- **Value type tests** covering all Sass value operations
- **Compiler tests** for both sync and async compilation
- **Protocol tests** for message handling and edge cases
- **Integration tests** with real Sass compilation
- **Performance benchmarks** for critical code paths

#### Development Tools
- **Modern Python tooling** with uv for dependency management
- **Code quality tools** (black, isort, ruff, mypy)
- **Comprehensive linting** and type checking
- **Test coverage reporting** with pytest-cov
- **Development workflow** with pre-commit hooks

### Breaking Changes
- None (initial release)

### Migration Guide
- None (initial release)

### Known Issues
- None currently identified

### Contributors
- Harvey McQueen - Initial implementation and architecture
- Complete protocol implementation following Embedded Sass specification
- Comprehensive value system with full Sass type support
- High-performance async/sync compiler implementations
- Extensive testing and documentation

---

## Release Notes Template

### [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Now removed features

### Fixed
- Bug fixes

### Security
- Vulnerability fixes
