"""
Tests for SassBoolean value type.
"""

import pytest
from dart_sass.value.boolean import SassBoolean, sass_true, sass_false


class TestSassBoolean:
    """Test cases for SassBoolean."""
    
    def test_singleton_instances(self):
        """Test that sass_true and sass_false are singleton instances."""
        assert isinstance(sass_true, SassBoolean)
        assert isinstance(sass_false, SassBoolean)
        assert sass_true is not sass_false
        
        # Test that we can't create new instances
        with pytest.raises(TypeError):
            SassBoolean(True)
    
    def test_value_property(self):
        """Test the value property."""
        assert sass_true.value is True
        assert sass_false.value is False
    
    def test_is_truthy(self):
        """Test the is_truthy property."""
        assert sass_true.is_truthy is True
        assert sass_false.is_truthy is False
    
    def test_separator_and_brackets(self):
        """Test list-related properties."""
        assert sass_true.separator is None
        assert sass_false.separator is None
        assert sass_true.has_brackets is False
        assert sass_false.has_brackets is False
    
    def test_equality(self):
        """Test equality comparison."""
        assert sass_true == sass_true
        assert sass_false == sass_false
        assert sass_true != sass_false
        assert sass_false != sass_true
        
        # Test against other types
        assert sass_true != True
        assert sass_false != False
        assert sass_true != "true"
        assert sass_false != None
    
    def test_hash(self):
        """Test hash functionality."""
        assert hash(sass_true) == hash(sass_true)
        assert hash(sass_false) == hash(sass_false)
        assert hash(sass_true) != hash(sass_false)
        
        # Test that they can be used in sets and dicts
        bool_set = {sass_true, sass_false}
        assert len(bool_set) == 2
        
        bool_dict = {sass_true: "true", sass_false: "false"}
        assert bool_dict[sass_true] == "true"
        assert bool_dict[sass_false] == "false"
    
    def test_string_representation(self):
        """Test string conversion."""
        assert str(sass_true) == "true"
        assert str(sass_false) == "false"
    
    def test_repr(self):
        """Test debug representation."""
        assert repr(sass_true) == "SassBoolean(True)"
        assert repr(sass_false) == "SassBoolean(False)"
    
    def test_assert_boolean(self):
        """Test assert_boolean method."""
        assert sass_true.assert_boolean() is sass_true
        assert sass_false.assert_boolean() is sass_false
        
        assert sass_true.assert_boolean("test") is sass_true
        assert sass_false.assert_boolean("test") is sass_false
