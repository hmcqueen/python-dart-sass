"""
Tests for SassList value type.
"""

import pytest
from dart_sass.value.list import SassList, ListSeparator
from dart_sass.value.string import SassString
from dart_sass.value.number import SassNumber
from dart_sass.value.boolean import sass_true, sass_false


class TestSassList:
    """Test cases for SassList."""
    
    def test_constructor_basic(self):
        """Test basic list construction."""
        # Empty list
        empty = SassList([])
        assert len(empty) == 0
        assert empty.contents == []
        assert empty.separator_enum == ListSeparator.COMMA  # Default
        assert empty.has_brackets is False  # Default
        
        # List with elements
        elements = [SassString("a"), SassNumber(1), sass_true]
        list_val = SassList(elements)
        assert len(list_val) == 3
        assert list_val.contents == elements
    
    def test_constructor_with_separator(self):
        """Test list construction with different separators."""
        elements = [SassString("a"), SassString("b")]
        
        # Comma separator
        comma_list = SassList(elements, ListSeparator.COMMA)
        assert comma_list.separator_enum == ListSeparator.COMMA
        assert comma_list.separator == ','
        
        # Space separator
        space_list = SassList(elements, ListSeparator.SPACE)
        assert space_list.separator_enum == ListSeparator.SPACE
        assert space_list.separator == ' '
        
        # Slash separator
        slash_list = SassList(elements, ListSeparator.SLASH)
        assert slash_list.separator_enum == ListSeparator.SLASH
        assert slash_list.separator == '/'
        
        # Undecided separator
        undecided_list = SassList(elements, ListSeparator.UNDECIDED)
        assert undecided_list.separator_enum == ListSeparator.UNDECIDED
        assert undecided_list.separator is None
    
    def test_constructor_with_brackets(self):
        """Test list construction with brackets (Node.js hasBrackets compatibility)."""
        elements = [SassString("a"), SassString("b")]
        
        # Without brackets (default)
        no_brackets = SassList(elements)
        assert no_brackets.has_brackets is False
        
        # With brackets
        with_brackets = SassList(elements, brackets=True)
        assert with_brackets.has_brackets is True
        
        # Explicit no brackets
        explicit_no_brackets = SassList(elements, brackets=False)
        assert explicit_no_brackets.has_brackets is False
    
    def test_node_js_properties(self):
        """Test Node.js-compatible properties."""
        elements = [SassString("a"), SassNumber(1)]
        list_val = SassList(elements, ListSeparator.SPACE, brackets=True)
        
        # Test has_brackets property (matches Node.js hasBrackets)
        assert list_val.has_brackets is True
        
        # Test separator property (matches Node.js separator)
        assert list_val.separator == ' '
        
        # Test contents property
        assert list_val.contents == elements
        
        # Test separator_enum for internal use
        assert list_val.separator_enum == ListSeparator.SPACE
    
    def test_base_value_properties(self):
        """Test inherited Value properties."""
        list_val = SassList([SassString("test")])
        
        # Test is_truthy (lists are always truthy in Sass)
        assert list_val.is_truthy is True
        
        # Test separator property (inherited from Value)
        assert list_val.separator == ','  # Default comma separator
        
        # Test has_brackets property (inherited from Value)
        assert list_val.has_brackets is False  # Default no brackets
    
    def test_list_access(self):
        """Test list element access."""
        elements = [SassString("a"), SassNumber(42), sass_true]
        list_val = SassList(elements)
        
        # Test length
        assert len(list_val) == 3
        
        # Test indexing
        assert list_val[0] == SassString("a")
        assert list_val[1] == SassNumber(42)
        assert list_val[2] == sass_true
        
        # Test iteration
        iterated = list(list_val)
        assert iterated == elements
        
        # Test contents property returns copy
        contents = list_val.contents
        contents.append(sass_false)
        assert len(list_val) == 3  # Original unchanged
    
    def test_equality(self):
        """Test list equality comparison."""
        elements1 = [SassString("a"), SassNumber(1)]
        elements2 = [SassString("a"), SassNumber(1)]
        elements3 = [SassString("b"), SassNumber(1)]
        
        list1 = SassList(elements1, ListSeparator.COMMA, brackets=False)
        list2 = SassList(elements2, ListSeparator.COMMA, brackets=False)
        list3 = SassList(elements1, ListSeparator.SPACE, brackets=False)  # Different separator
        list4 = SassList(elements1, ListSeparator.COMMA, brackets=True)   # Different brackets
        list5 = SassList(elements3, ListSeparator.COMMA, brackets=False)  # Different contents
        
        # Same contents, separator, and brackets
        assert list1 == list2
        assert hash(list1) == hash(list2)
        
        # Different separator
        assert list1 != list3
        
        # Different brackets
        assert list1 != list4
        
        # Different contents
        assert list1 != list5
        
        # Not equal to other types
        assert list1 != elements1
        assert list1 != "a,1"
    
    def test_string_representation(self):
        """Test string representation."""
        # Empty list without brackets
        empty = SassList([])
        assert str(empty) == "()"
        
        # Empty list with brackets
        empty_brackets = SassList([], brackets=True)
        assert str(empty_brackets) == "[]"
        
        # Single element comma list (special case)
        single_comma = SassList([SassString("a")], ListSeparator.COMMA)
        assert str(single_comma) == "(\"a\",)"
        
        # Multiple elements comma separated
        comma_list = SassList([SassString("a"), SassString("b")], ListSeparator.COMMA)
        assert str(comma_list) == "\"a\",\"b\""
        
        # Space separated
        space_list = SassList([SassString("a"), SassString("b")], ListSeparator.SPACE)
        assert str(space_list) == "\"a\" \"b\""
        
        # With brackets
        bracket_list = SassList([SassString("a"), SassString("b")], brackets=True)
        assert str(bracket_list) == "[\"a\",\"b\"]"
        
        # Slash separated
        slash_list = SassList([SassNumber(1), SassNumber(2)], ListSeparator.SLASH)
        assert str(slash_list) == "1/2"
    
    def test_repr(self):
        """Test Python representation."""
        elements = [SassString("a")]
        list_val = SassList(elements, ListSeparator.SPACE, brackets=True)
        
        expected = "SassList([SassString('a', quoted=True)], separator=<ListSeparator.SPACE: 'space'>, brackets=True)"
        assert repr(list_val) == expected
    
    def test_nested_lists(self):
        """Test lists containing other lists."""
        inner_list = SassList([SassNumber(1), SassNumber(2)])
        outer_list = SassList([SassString("a"), inner_list, SassString("b")])
        
        assert len(outer_list) == 3
        assert outer_list[1] == inner_list
        assert len(outer_list[1]) == 2
    
    def test_mixed_value_types(self):
        """Test lists with mixed value types."""
        mixed = SassList([
            SassString("text"),
            SassNumber(42, 'px'),
            sass_true,
            sass_false,
            SassList([SassNumber(1), SassNumber(2)])  # Nested list
        ])
        
        assert len(mixed) == 5
        assert isinstance(mixed[0], SassString)
        assert isinstance(mixed[1], SassNumber)
        assert mixed[2] is sass_true
        assert mixed[3] is sass_false
        assert isinstance(mixed[4], SassList)
    
    def test_immutability(self):
        """Test that lists are immutable."""
        elements = [SassString("a"), SassNumber(1)]
        list_val = SassList(elements)
        
        # Contents should be a copy
        original_contents = list_val.contents
        original_contents.append(sass_true)
        assert len(list_val) == 2  # Original unchanged
        
        # Properties should be read-only
        with pytest.raises(AttributeError):
            list_val.separator_enum = ListSeparator.SPACE
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Single element with different separators
        single_space = SassList([SassString("a")], ListSeparator.SPACE)
        assert str(single_space) == "\"a\""
        
        single_slash = SassList([SassString("a")], ListSeparator.SLASH)
        assert str(single_slash) == "\"a\""
        
        # Undecided separator with single element
        single_undecided = SassList([SassString("a")], ListSeparator.UNDECIDED)
        assert single_undecided.separator is None
        assert str(single_undecided) == "\"a\""
