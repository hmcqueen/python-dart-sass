"""
Tests for importer registry.
"""

import pytest
import tempfile
import os
from pathlib import Path
from dart_sass.importer_registry import (
    ImporterRegistry, 
    ImporterResult,
    Importer,
    FileImporter
)
from dart_sass.canonicalize_context import CanonicalizeContext


class TestImporterRegistry:
    """Test cases for importer registry."""
    
    def test_constructor_with_importers(self):
        """Test constructor with importers (Node.js pattern)."""
        class TestImporter:
            def canonicalize(self, url: str, context: CanonicalizeContext) -> str:
                if url == "test:":
                    return "test://example"
                return None
            
            def load(self, canonical_url: str) -> ImporterResult:
                if canonical_url == "test://example":
                    return ImporterResult("/* test */", "scss")
                return None
        
        test_importer = TestImporter()
        
        # Use Node.js constructor pattern
        registry = ImporterRegistry({
            'importers': [test_importer]
        })
        
        assert len(registry.importers) == 1
        assert 0 in registry._importers_by_id
        assert registry._importers_by_id[0] == test_importer
    
    def test_constructor_with_load_paths(self):
        """Test constructor with load paths (Node.js pattern)."""
        registry = ImporterRegistry({
            'load_paths': ['/test/path', '/another/path']
        })
        
        assert len(registry.importers) == 2
        # Check that load paths are converted to protobuf importers
        assert registry.importers[0].path == str(Path('/test/path').resolve())
        assert registry.importers[1].path == str(Path('/another/path').resolve())
    
    def test_constructor_with_mixed_options(self):
        """Test constructor with both importers and load paths."""
        class TestImporter:
            def canonicalize(self, url: str, context: CanonicalizeContext) -> str:
                return None
            
            def load(self, canonical_url: str) -> ImporterResult:
                return None
        
        registry = ImporterRegistry({
            'importers': [TestImporter()],
            'load_paths': ['/test/path']
        })
        
        assert len(registry.importers) == 2  # 1 importer + 1 load path
    
    def test_register_regular_importer(self):
        """Test register method with regular importer (Node.js pattern)."""
        class TestImporter:
            def canonicalize(self, url: str, context: CanonicalizeContext) -> str:
                return "test://canonical"
            
            def load(self, canonical_url: str) -> ImporterResult:
                return ImporterResult("/* test */", "scss")
        
        registry = ImporterRegistry()
        importer = TestImporter()
        
        proto_importer = registry.register(importer)
        
        # Check protobuf structure (like Node.js)
        assert hasattr(proto_importer, 'importer_id')
        assert proto_importer.importer_id == 0
        assert 0 in registry._importers_by_id
        assert registry._importers_by_id[0] == importer
    
    def test_register_file_importer(self):
        """Test register method with file importer (Node.js pattern)."""
        class TestFileImporter:
            def find_file_url(self, url: str, context: CanonicalizeContext) -> str:
                return f"file:///test/{url}.scss"
        
        registry = ImporterRegistry()
        importer = TestFileImporter()
        
        proto_importer = registry.register(importer)
        
        # Check protobuf structure (like Node.js)
        assert hasattr(proto_importer, 'file_importer_id')
        assert proto_importer.file_importer_id == 0
        assert 0 in registry._file_importers_by_id
        assert registry._file_importers_by_id[0] == importer
    
    def test_register_importer_with_non_canonical_scheme(self):
        """Test register with non-canonical scheme (Node.js pattern)."""
        class TestImporter:
            non_canonical_scheme = "custom"
            
            def canonicalize(self, url: str, context: CanonicalizeContext) -> str:
                return None
            
            def load(self, canonical_url: str) -> ImporterResult:
                return None
        
        registry = ImporterRegistry()
        proto_importer = registry.register(TestImporter())
        
        # Check non-canonical scheme is set (like Node.js)
        assert "custom" in proto_importer.non_canonical_scheme
    
    def test_register_importer_with_multiple_non_canonical_schemes(self):
        """Test register with multiple non-canonical schemes."""
        class TestImporter:
            non_canonical_scheme = ["custom1", "custom2"]
            
            def canonicalize(self, url: str, context: CanonicalizeContext) -> str:
                return None
            
            def load(self, canonical_url: str) -> ImporterResult:
                return None
        
        registry = ImporterRegistry()
        proto_importer = registry.register(TestImporter())
        
        # Check multiple schemes are set
        assert "custom1" in proto_importer.non_canonical_scheme
        assert "custom2" in proto_importer.non_canonical_scheme
    
    def test_register_invalid_importer(self):
        """Test error when registering invalid importer (Node.js pattern)."""
        registry = ImporterRegistry()
        
        class InvalidImporter:
            # Has both canonicalize and find_file_url (invalid)
            def canonicalize(self, url: str, context: CanonicalizeContext) -> str:
                return None
            
            def find_file_url(self, url: str, context: CanonicalizeContext) -> str:
                return None
        
        with pytest.raises(Exception, match="may not contain both canonicalize\\(\\) and find_file_url\\(\\)"):
            registry.register(InvalidImporter())
    
    def test_register_importer_without_required_methods(self):
        """Test error when importer lacks required methods."""
        registry = ImporterRegistry()
        
        class IncompleteImporter:
            pass  # No required methods
        
        with pytest.raises(Exception, match="must have either canonicalize\\(\\) or find_file_url\\(\\)"):
            registry.register(IncompleteImporter())
    
    def test_empty_constructor(self):
        """Test constructor with no options (Node.js pattern)."""
        registry = ImporterRegistry()
        
        assert len(registry.importers) == 0
        assert len(registry._importers_by_id) == 0
        assert len(registry._file_importers_by_id) == 0
        assert registry._next_id == 0
    
    def test_constructor_with_none_options(self):
        """Test constructor with None options."""
        registry = ImporterRegistry(None)
        
        assert len(registry.importers) == 0
        assert len(registry._importers_by_id) == 0
        assert len(registry._file_importers_by_id) == 0
    
    def test_id_assignment(self):
        """Test that IDs are assigned incrementally (Node.js pattern)."""
        class TestImporter:
            def canonicalize(self, url: str, context: CanonicalizeContext) -> str:
                return None
            
            def load(self, canonical_url: str) -> ImporterResult:
                return None
        
        registry = ImporterRegistry()
        
        proto1 = registry.register(TestImporter())
        proto2 = registry.register(TestImporter())
        
        assert proto1.importer_id == 0
        assert proto2.importer_id == 1
        assert registry._next_id == 2


class TestImporterRegistryProtocolMethods:
    """Test the protocol methods that handle requests from the compiler."""
    
    def test_canonicalize_success(self):
        """Test successful canonicalize request."""
        class TestImporter:
            def canonicalize(self, url: str, context: CanonicalizeContext) -> str:
                if url == "test:example":
                    return "test://canonical"
                return None
            
            def load(self, canonical_url: str) -> ImporterResult:
                return None
        
        registry = ImporterRegistry({'importers': [TestImporter()]})
        
        # Create mock request (would normally come from protobuf)
        class MockRequest:
            importer_id = 0
            url = "test:example"
            containing_url = None
            from_import = False
        
        response = registry.canonicalize(MockRequest())
        
        # Should be successful (no error field)
        assert not hasattr(response, 'error') or not response.error
        assert response.url == "test://canonical"
    
    def test_canonicalize_no_result(self):
        """Test canonicalize when importer returns None."""
        class TestImporter:
            def canonicalize(self, url: str, context: CanonicalizeContext) -> str:
                return None  # Can't handle this URL
            
            def load(self, canonical_url: str) -> ImporterResult:
                return None
        
        registry = ImporterRegistry({'importers': [TestImporter()]})
        
        class MockRequest:
            importer_id = 0
            url = "unknown:example"
            containing_url = None
            from_import = False
        
        response = registry.canonicalize(MockRequest())
        
        # Should be successful but with no URL
        assert not hasattr(response, 'error') or not response.error
        assert not response.url
    
    def test_canonicalize_unknown_importer(self):
        """Test canonicalize with unknown importer ID."""
        registry = ImporterRegistry()
        
        class MockRequest:
            importer_id = 999  # Non-existent ID
            url = "test:example"
            containing_url = None
            from_import = False
        
        response = registry.canonicalize(MockRequest())
        
        # Should return error
        assert response.error
        assert "Unknown CanonicalizeRequest.importer_id" in response.error
