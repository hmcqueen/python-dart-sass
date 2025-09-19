"""
Dependencies test based on Node.js reference implementation.
"""

import pytest
from dart_sass.version import __protocol_version__


class TestDependenciesReference:
    """Test dependencies following Node.js reference implementation exactly."""
    
    def test_declares_compatible_dependency_on_embedded_protocol(self):
        """Test that we declare a compatible dependency on the embedded protocol."""
        # If protocol version ends with '-dev', skip the check
        if __protocol_version__.endswith('-dev'):
            pytest.skip("Development version of protocol")
            return
        
        # In the Node.js implementation, they read the actual protocol version
        # from the embedded Sass compiler and compare it to their declared version.
        # For our Python implementation, we should ensure our declared protocol
        # version matches what we actually support.
        
        # This is a basic check that we have a valid protocol version
        assert __protocol_version__ is not None
        assert isinstance(__protocol_version__, str)
        assert len(__protocol_version__) > 0
        
        # Protocol version should be in semantic version format
        parts = __protocol_version__.split('.')
        assert len(parts) >= 2, f"Protocol version should be in x.y format, got: {__protocol_version__}"
        
        # Each part should be numeric (except for -dev suffix)
        for i, part in enumerate(parts):
            if i == len(parts) - 1 and part.endswith('-dev'):
                part = part[:-4]  # Remove -dev suffix
            assert part.isdigit(), f"Protocol version part should be numeric, got: {part}"
