"""
Tests for SassString value type.
"""

import pytest
from dart_sass.value.string import SassString


class TestSassString:
    """Test cases for SassString."""
    
    def test_constructor_with_text(self):
        """Test constructor with text argument."""
        # Default quoted
        s1 = SassString("hello")
        assert s1.text == "hello"
        assert s1.has_quotes is True
        
        # Explicitly quoted
        s2 = SassString("world", quoted=True)
        assert s2.text == "world"
        assert s2.has_quotes is True
        
        # Unquoted
        s3 = SassString("unquoted", quoted=False)
        assert s3.text == "unquoted"
        assert s3.has_quotes is False
    
    def test_empty_string_constructor(self):
        """Test empty string handling with constructor."""
        empty_quoted = SassString("")
        assert empty_quoted.text == ""
        assert empty_quoted.has_quotes is True
        
        empty_unquoted = SassString("", quoted=False)
        assert empty_unquoted.text == ""
        assert empty_unquoted.has_quotes is False
    
    def test_empty_static_method(self):
        """Test SassString.empty() static method (Node.js compatibility)."""
        # Default quoted empty
        empty_quoted = SassString.empty()
        assert empty_quoted.text == ""
        assert empty_quoted.has_quotes is True
        
        # Explicitly quoted empty
        empty_quoted_explicit = SassString.empty(quoted=True)
        assert empty_quoted_explicit.text == ""
        assert empty_quoted_explicit.has_quotes is True
        
        # Unquoted empty
        empty_unquoted = SassString.empty(quoted=False)
        assert empty_unquoted.text == ""
        assert empty_unquoted.has_quotes is False
    
    def test_node_js_properties(self):
        """Test Node.js-compatible properties."""
        quoted = SassString("test")
        unquoted = SassString("test", quoted=False)
        
        # Test has_quotes property (matches Node.js hasQuotes)
        assert quoted.has_quotes is True
        assert unquoted.has_quotes is False
        
        # Test sass_length property (matches Node.js sassLength)
        assert quoted.sass_length == 4
        assert unquoted.sass_length == 4
        
        # Test with Unicode characters
        unicode_string = SassString("héllo")
        assert unicode_string.sass_length == 5
        
        # Test empty string length
        empty = SassString.empty()
        assert empty.sass_length == 0
    
    def test_base_value_properties(self):
        """Test inherited Value properties."""
        quoted = SassString("test")
        unquoted = SassString("test", quoted=False)
        
        # Test is_truthy (strings are always truthy in Sass)
        assert quoted.is_truthy is True
        assert unquoted.is_truthy is True
        
        # Test separator (strings don't have separators)
        assert quoted.separator is None
        assert unquoted.separator is None
        
        # Test has_brackets (strings don't have brackets)
        assert quoted.has_brackets is False
        assert unquoted.has_brackets is False
    
    def test_equality(self):
        """Test string equality comparison."""
        s1 = SassString("hello", quoted=True)
        s2 = SassString("hello", quoted=True)
        s3 = SassString("hello", quoted=False)
        s4 = SassString("world", quoted=True)
        
        # Same text and quotes
        assert s1 == s2
        assert hash(s1) == hash(s2)
        
        # Same text, different quotes
        assert s1 != s3
        assert hash(s1) != hash(s3)
        
        # Different text, same quotes
        assert s1 != s4
        assert hash(s1) != hash(s4)
        
        # Not equal to other types
        assert s1 != "hello"
        assert s1 != 42
        assert s1 != None
    
    def test_string_representation(self):
        """Test string representation."""
        # Quoted strings should include quotes
        quoted = SassString("hello world", quoted=True)
        assert str(quoted) == '"hello world"'
        
        # Unquoted strings should not include quotes
        unquoted = SassString("hello", quoted=False)
        assert str(unquoted) == "hello"
        
        # Test quote escaping
        with_quotes = SassString('say "hello"', quoted=True)
        assert str(with_quotes) == '"say \\"hello\\""'
        
        # Empty strings
        empty_quoted = SassString.empty(quoted=True)
        assert str(empty_quoted) == '""'
        
        empty_unquoted = SassString.empty(quoted=False)
        assert str(empty_unquoted) == ""
    
    def test_repr(self):
        """Test Python representation."""
        quoted = SassString("hello", quoted=True)
        assert repr(quoted) == "SassString('hello', quoted=True)"
        
        unquoted = SassString("world", quoted=False)
        assert repr(unquoted) == "SassString('world', quoted=False)"
    
    def test_special_characters(self):
        """Test strings with special characters."""
        # Unicode characters
        unicode_str = SassString("héllo wörld", quoted=True)
        assert unicode_str.text == "héllo wörld"
        assert unicode_str.sass_length == 11
        
        # Newlines and tabs
        multiline = SassString("line1\nline2\ttab", quoted=True)
        assert multiline.text == "line1\nline2\ttab"
        assert multiline.sass_length == 15
        
        # Empty string edge cases
        whitespace = SassString("   ", quoted=False)
        assert whitespace.text == "   "
        assert whitespace.sass_length == 3
    
    def test_immutability(self):
        """Test that strings are immutable."""
        original = SassString("test", quoted=True)
        
        # Properties should be read-only (no setters)
        with pytest.raises(AttributeError):
            original.text = "changed"
        
        with pytest.raises(AttributeError):
            original.has_quotes = False
