"""
Tests for SassNull value type.
"""

import pytest
from dart_sass.value.null import SassNull, sass_null


class TestSassNull:
    """Test cases for SassNull."""
    
    def test_singleton_instance(self):
        """Test that sass_null is a singleton instance."""
        assert isinstance(sass_null, SassNull)
        
        # Test that we can't create new instances
        with pytest.raises(TypeError):
            SassNull()
    
    def test_is_truthy(self):
        """Test the is_truthy property."""
        assert sass_null.is_truthy is False
    
    def test_separator_and_brackets(self):
        """Test list-related properties."""
        assert sass_null.separator is None
        assert sass_null.has_brackets is False
    
    def test_equality(self):
        """Test equality comparison."""
        assert sass_null == sass_null
        
        # Test against other types
        assert sass_null != None
        assert sass_null != "null"
        assert sass_null != False
        assert sass_null != 0
    
    def test_hash(self):
        """Test hash functionality."""
        assert hash(sass_null) == hash(sass_null)
        
        # Test that it can be used in sets and dicts
        null_set = {sass_null}
        assert len(null_set) == 1
        
        null_dict = {sass_null: "null"}
        assert null_dict[sass_null] == "null"
    
    def test_string_representation(self):
        """Test string conversion."""
        assert str(sass_null) == "null"
    
    def test_repr(self):
        """Test debug representation."""
        assert repr(sass_null) == "SassNull()"
