"""
Tests for SassNumber value type.
"""

import pytest
from dart_sass.value.number import SassNumber


class TestSassNumber:
    """Test cases for SassNumber."""
    
    def test_constructor_unitless(self):
        """Test constructor with unitless numbers."""
        num = SassNumber(42.5)
        assert num.value == 42.5
        assert num.numerator_units == []
        assert num.denominator_units == []
        assert num.has_units is False
        assert num.unit == ""  # Backward compatibility
    
    def test_constructor_simple_unit(self):
        """Test constructor with simple unit string (Node.js pattern)."""
        num = SassNumber(10, 'px')
        assert num.value == 10
        assert num.numerator_units == ['px']
        assert num.denominator_units == []
        assert num.has_units is True
        assert num.unit == 'px'  # Backward compatibility
    
    def test_constructor_complex_units(self):
        """Test constructor with complex units (Node.js pattern)."""
        num = SassNumber(5, {
            'numerator_units': ['px', 'em'],
            'denominator_units': ['s', 'ms']
        })
        assert num.value == 5
        assert num.numerator_units == ['px', 'em']
        assert num.denominator_units == ['s', 'ms']
        assert num.has_units is True
    
    def test_constructor_unit_simplification(self):
        """Test that matching numerator/denominator units are simplified."""
        # Units that cancel out
        num = SassNumber(10, {
            'numerator_units': ['px', 'em'],
            'denominator_units': ['px', 's']
        })
        assert num.value == 10
        assert num.numerator_units == ['em']
        assert num.denominator_units == ['s']
        assert num.has_units is True
    
    def test_node_js_properties(self):
        """Test Node.js-compatible properties."""
        # Test is_int property (matches Node.js isInt)
        integer_num = SassNumber(42)
        float_num = SassNumber(42.5)
        almost_int = SassNumber(42.000000000001)  # Within 1e-11 threshold
        
        assert integer_num.is_int is True
        assert float_num.is_int is False
        assert almost_int.is_int is True  # Fuzzy comparison
        
        # Test as_int property (matches Node.js asInt)
        assert integer_num.as_int == 42
        assert float_num.as_int is None
        assert almost_int.as_int == 42
        
        # Test numerator_units and denominator_units (matches Node.js)
        complex_num = SassNumber(1, {
            'numerator_units': ['px', 'em'],
            'denominator_units': ['s']
        })
        assert complex_num.numerator_units == ['px', 'em']
        assert complex_num.denominator_units == ['s']
        
        # Test has_units property (matches Node.js hasUnits)
        unitless = SassNumber(42)
        with_units = SassNumber(42, 'px')
        assert unitless.has_units is False
        assert with_units.has_units is True
    
    def test_node_js_methods(self):
        """Test Node.js-compatible methods."""
        # Test assert_number method (matches Node.js assertNumber)
        num = SassNumber(42)
        assert num.assert_number() is num
        
        # Test assert_int method (matches Node.js assertInt)
        integer_num = SassNumber(42)
        float_num = SassNumber(42.5)
        
        assert integer_num.assert_int() == 42
        
        with pytest.raises(ValueError, match="is not an int"):
            float_num.assert_int()
        
        # Test assert_int with name parameter
        with pytest.raises(ValueError, match="argument: \\$width"):
            float_num.assert_int("width")
        
        # Test assert_in_range method (matches Node.js assertInRange)
        num = SassNumber(50)
        assert num.assert_in_range(0, 100) == 50
        assert num.assert_in_range(50, 100) == 50  # Exact boundary
        assert num.assert_in_range(0, 50) == 50    # Exact boundary
        
        with pytest.raises(ValueError, match="must be between 0 and 10"):
            num.assert_in_range(0, 10)
        
        # Test assert_in_range with name parameter
        with pytest.raises(ValueError, match="argument: \\$opacity"):
            num.assert_in_range(0, 1, "opacity")
    
    def test_base_value_properties(self):
        """Test inherited Value properties."""
        num = SassNumber(42, 'px')
        
        # Test is_truthy (numbers are always truthy in Sass)
        assert num.is_truthy is True
        
        # Test separator (numbers don't have separators)
        assert num.separator is None
        
        # Test has_brackets (numbers don't have brackets)
        assert num.has_brackets is False
    
    def test_equality(self):
        """Test number equality comparison."""
        num1 = SassNumber(42.5, 'px')
        num2 = SassNumber(42.5, 'px')
        num3 = SassNumber(42.5, 'em')
        num4 = SassNumber(43.5, 'px')
        
        # Same value and units
        assert num1 == num2
        assert hash(num1) == hash(num2)
        
        # Same value, different units
        assert num1 != num3
        
        # Different value, same units
        assert num1 != num4
        
        # Fuzzy equality for floating point
        almost_same = SassNumber(42.500000000001, 'px')  # Within 1e-11 threshold
        assert num1 == almost_same
        
        # Not equal to other types
        assert num1 != 42.5
        assert num1 != "42.5px"
    
    def test_string_representation(self):
        """Test string representation."""
        # Unitless number
        unitless = SassNumber(42.5)
        assert str(unitless) == "42.5"
        
        # Number with simple unit
        with_unit = SassNumber(10, 'px')
        assert str(with_unit) == "10px"
        
        # Number with complex units
        complex_num = SassNumber(5, {
            'numerator_units': ['px', 'em'],
            'denominator_units': ['s']
        })
        assert str(complex_num) == "5pxem/s"
        
        # Integer display
        integer = SassNumber(42)
        assert str(integer) == "42"
    
    def test_repr(self):
        """Test Python representation."""
        unitless = SassNumber(42)
        assert repr(unitless) == "SassNumber(42)"
        
        simple_unit = SassNumber(10, 'px')
        assert repr(simple_unit) == "SassNumber(10, 'px')"
        
        complex_units = SassNumber(5, {
            'numerator_units': ['px'],
            'denominator_units': ['s']
        })
        expected = "SassNumber(5, {'numerator_units': ['px'], 'denominator_units': ['s']})"
        assert repr(complex_units) == expected
    
    def test_edge_cases(self):
        """Test edge cases and special values."""
        # Zero
        zero = SassNumber(0)
        assert zero.value == 0
        assert zero.is_int is True
        assert zero.as_int == 0
        
        # Negative numbers
        negative = SassNumber(-42.5, 'px')
        assert negative.value == -42.5
        assert negative.is_int is False
        
        # Very small numbers (fuzzy int detection)
        tiny_diff = SassNumber(42.000000000001)  # Within 1e-11 threshold
        assert tiny_diff.is_int is True
        assert tiny_diff.as_int == 42
        
        # Large numbers
        large = SassNumber(1e10, 'px')
        assert large.value == 1e10
        assert large.numerator_units == ['px']
    
    def test_immutability(self):
        """Test that numbers are immutable."""
        num = SassNumber(42, 'px')
        
        # Properties should be read-only
        with pytest.raises(AttributeError):
            num.value = 43
        
        # Unit lists should be copies (not references)
        units = num.numerator_units
        units.append('em')
        assert num.numerator_units == ['px']  # Original unchanged
    
    def test_backward_compatibility(self):
        """Test backward compatibility with simple unit interface."""
        # Simple unit interface should still work
        num = SassNumber(42, 'px')
        assert num.unit == 'px'
        
        # Complex units should return first numerator unit
        complex_num = SassNumber(10, {
            'numerator_units': ['px', 'em'],
            'denominator_units': ['s']
        })
        assert complex_num.unit == 'px'
        
        # Unitless should return empty string
        unitless = SassNumber(42)
        assert unitless.unit == ""
