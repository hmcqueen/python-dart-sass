"""
Utils tests based on Node.js reference implementation.
"""

import pytest
from pathlib import Path
from urllib.parse import quote
from dart_sass.utils import path_to_url_string


class TestUtilsReference:
    """Test utils following Node.js reference implementation exactly."""
    
    def test_encode_relative_path_like_pathToFileURL(self):
        """Test encoding relative path like Node.js pathToFileURL."""
        # Skip charcodes 0-32 to work around Node trailing whitespace regression
        # https://github.com/nodejs/node/issues/51167
        for i in range(33, 128):
            char = chr(i)
            filename = f"{i}-{char}"
            
            # Our implementation should match URL encoding behavior
            result = path_to_url_string(filename)
            
            # Expected behavior: URL encode special characters
            expected = quote(filename, safe='-._~')
            
            assert result == expected, f"Failed for character {i} ({char}): got {result}, expected {expected}"
    
    def test_encode_percent_encoded_string_like_pathToFileURL(self):
        """Test encoding percent encoded string like Node.js pathToFileURL."""
        for i in range(128):
            # Test lowercase percent encoding
            lowercase = f"%{i:02x}" if i >= 16 else f"%0{i:x}"
            result_lower = path_to_url_string(lowercase)
            
            # Test uppercase percent encoding  
            uppercase = lowercase.upper()
            result_upper = path_to_url_string(uppercase)
            
            # Both should be handled consistently
            # Percent-encoded strings should generally be preserved
            expected_lower = lowercase
            expected_upper = uppercase
            
            assert result_lower == expected_lower, f"Failed for lowercase %{i:02x}: got {result_lower}, expected {expected_lower}"
            assert result_upper == expected_upper, f"Failed for uppercase %{i:02X}: got {result_upper}, expected {expected_upper}"
