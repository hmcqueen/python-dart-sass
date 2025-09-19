"""
Tests for value converter between Python and protobuf.
"""

import pytest
from dart_sass.value_converter import Protofier, to_proto, from_proto
from dart_sass.function_registry import FunctionRegistry
from dart_sass.value.boolean import SassBoolean, sass_true, sass_false
from dart_sass.value.null import SassNull, sass_null
from dart_sass.value.string import SassString
from dart_sass.value.number import SassNumber
from dart_sass.value.list import SassList, ListSeparator
from dart_sass.value.map import SassMap
from dart_sass.value.color import SassColor
from dart_sass.vendor import embedded_sass_pb2 as proto
from dart_sass.exception import CompileException


class TestProtofier:
    """Test cases for Protofier class (Node.js compatibility)."""
    
    def test_protofier_constructor(self):
        """Test Protofier constructor with FunctionRegistry."""
        registry = FunctionRegistry()
        protofier = Protofier(registry)
        
        assert protofier.functions is registry
        assert protofier.accessed_argument_lists == []
    
    def test_string_conversion(self):
        """Test string value conversion."""
        registry = FunctionRegistry()
        protofier = Protofier(registry)
        
        # Test quoted string
        quoted_string = SassString("hello world", quoted=True)
        proto_quoted = protofier.protofy(quoted_string)
        assert proto_quoted.string.text == "hello world"
        assert proto_quoted.string.quoted == True
        
        back_quoted = protofier.deprotofy(proto_quoted)
        assert isinstance(back_quoted, SassString)
        assert back_quoted.text == "hello world"
        assert back_quoted.has_quotes == True
        
        # Test unquoted string
        unquoted_string = SassString("unquoted", quoted=False)
        proto_unquoted = protofier.protofy(unquoted_string)
        assert proto_unquoted.string.text == "unquoted"
        assert proto_unquoted.string.quoted == False
        
        back_unquoted = protofier.deprotofy(proto_unquoted)
        assert isinstance(back_unquoted, SassString)
        assert back_unquoted.text == "unquoted"
        assert back_unquoted.has_quotes == False
    
    def test_string_empty_conversion(self):
        """Test empty string conversion using SassString.empty()."""
        registry = FunctionRegistry()
        protofier = Protofier(registry)
        
        # Test empty quoted string
        empty_quoted = SassString.empty(quoted=True)
        proto_empty = protofier.protofy(empty_quoted)
        back_empty = protofier.deprotofy(proto_empty)
        
        assert back_empty.text == ""
        assert back_empty.has_quotes == True
        
        # Test empty unquoted string
        empty_unquoted = SassString.empty(quoted=False)
        proto_empty_unq = protofier.protofy(empty_unquoted)
        back_empty_unq = protofier.deprotofy(proto_empty_unq)
        
        assert back_empty_unq.text == ""
        assert back_empty_unq.has_quotes == False
    
    def test_number_conversion(self):
        """Test number value conversion with Node.js-compatible units."""
        registry = FunctionRegistry()
        protofier = Protofier(registry)
        
        # Test unitless number
        unitless = SassNumber(42.5)
        proto_unitless = protofier.protofy(unitless)
        assert proto_unitless.number.value == 42.5
        assert len(proto_unitless.number.numerators) == 0
        assert len(proto_unitless.number.denominators) == 0
        
        back_unitless = protofier.deprotofy(proto_unitless)
        assert back_unitless.value == 42.5
        assert back_unitless.numerator_units == []
        assert back_unitless.denominator_units == []
        assert back_unitless.has_units == False
        
        # Test number with simple unit
        with_unit = SassNumber(10, 'px')
        proto_with_unit = protofier.protofy(with_unit)
        assert proto_with_unit.number.value == 10
        assert list(proto_with_unit.number.numerators) == ['px']
        assert len(proto_with_unit.number.denominators) == 0
        
        back_with_unit = protofier.deprotofy(proto_with_unit)
        assert back_with_unit.value == 10
        assert back_with_unit.numerator_units == ['px']
        assert back_with_unit.denominator_units == []
        assert back_with_unit.has_units == True
        
        # Test number with complex units
        complex_num = SassNumber(5, {
            'numerator_units': ['px', 'em'],
            'denominator_units': ['s']
        })
        proto_complex = protofier.protofy(complex_num)
        assert proto_complex.number.value == 5
        assert list(proto_complex.number.numerators) == ['px', 'em']
        assert list(proto_complex.number.denominators) == ['s']
        
        back_complex = protofier.deprotofy(proto_complex)
        assert back_complex.value == 5
        assert back_complex.numerator_units == ['px', 'em']
        assert back_complex.denominator_units == ['s']
        assert back_complex.has_units == True
    
    def test_color_conversion(self):
        """Test color value conversion with Node.js-compatible properties."""
        registry = FunctionRegistry()
        protofier = Protofier(registry)
        
        # Test RGB color
        rgb_color = SassColor(red=255, green=128, blue=0, alpha=0.8, space='rgb')
        proto_rgb = protofier.protofy(rgb_color)
        
        assert proto_rgb.color.space == "rgb"
        assert proto_rgb.color.channel1 == 255
        assert proto_rgb.color.channel2 == 128
        assert proto_rgb.color.channel3 == 0
        assert proto_rgb.color.alpha == 0.8
        
        back_rgb = protofier.deprotofy(proto_rgb)
        assert back_rgb.space == "rgb"
        assert back_rgb.channels_or_null == [255, 128, 0]
        assert back_rgb.alpha == 0.8
        assert back_rgb.is_channel_missing('alpha') == False
        
        # Test HSL color
        hsl_color = SassColor(hue=120, saturation=50, lightness=75, space='hsl')
        proto_hsl = protofier.protofy(hsl_color)
        back_hsl = protofier.deprotofy(proto_hsl)
        
        assert back_hsl.space == "hsl"
        assert back_hsl.channels_or_null == [120, 50, 75]
        
        # Test color with missing alpha
        no_alpha = SassColor(red=100, green=100, blue=100, space='rgb')
        proto_no_alpha = protofier.protofy(no_alpha)
        back_no_alpha = protofier.deprotofy(proto_no_alpha)
        
        assert back_no_alpha.is_channel_missing('alpha') == True
    
    def test_list_conversion(self):
        """Test list value conversion with Node.js-compatible properties."""
        registry = FunctionRegistry()
        protofier = Protofier(registry)
        
        # Test list with brackets
        elements = [SassString("a"), SassNumber(1), sass_true]
        sass_list = SassList(elements, ListSeparator.COMMA, brackets=True)
        proto_list = protofier.protofy(sass_list)
        
        assert proto_list.list.separator == proto.ListSeparator.COMMA
        assert proto_list.list.has_brackets == True
        assert len(proto_list.list.contents) == 3
        
        back_list = protofier.deprotofy(proto_list)
        assert back_list.separator == ','
        assert back_list.has_brackets == True
        assert len(back_list.contents) == 3
        assert back_list.contents[0].text == "a"
        assert back_list.contents[1].value == 1
        assert back_list.contents[2] is sass_true
        
        # Test different separators
        space_list = SassList([SassNumber(1), SassNumber(2)], ListSeparator.SPACE)
        proto_space = protofier.protofy(space_list)
        back_space = protofier.deprotofy(proto_space)
        assert back_space.separator == ' '
        
        slash_list = SassList([SassNumber(1), SassNumber(2)], ListSeparator.SLASH)
        proto_slash = protofier.protofy(slash_list)
        back_slash = protofier.deprotofy(proto_slash)
        assert back_slash.separator == '/'
    
    def test_singleton_conversion(self):
        """Test singleton value conversion."""
        registry = FunctionRegistry()
        protofier = Protofier(registry)
        
        # Test true
        proto_true = protofier.protofy(sass_true)
        assert proto_true.singleton == proto.SingletonValue.TRUE
        back_true = protofier.deprotofy(proto_true)
        assert back_true is sass_true
        
        # Test false
        proto_false = protofier.protofy(sass_false)
        assert proto_false.singleton == proto.SingletonValue.FALSE
        back_false = protofier.deprotofy(proto_false)
        assert back_false is sass_false
        
        # Test null
        proto_null = protofier.protofy(sass_null)
        assert proto_null.singleton == proto.SingletonValue.NULL
        back_null = protofier.deprotofy(proto_null)
        assert back_null is sass_null
    
    def test_map_conversion(self):
        """Test map value conversion."""
        registry = FunctionRegistry()
        protofier = Protofier(registry)
        
        sass_map = SassMap({
            SassString("key1"): SassNumber(10),
            SassString("key2"): sass_true
        })
        proto_map = protofier.protofy(sass_map)
        
        assert len(proto_map.map.entries) == 2
        
        back_map = protofier.deprotofy(proto_map)
        assert isinstance(back_map, SassMap)
        assert len(back_map.contents) == 2
        
        # Find entries by key
        key1 = SassString("key1")
        key2 = SassString("key2")
        
        assert key1 in back_map.contents
        assert isinstance(back_map.contents[key1], SassNumber)
        assert back_map.contents[key1].value == 10
        
        assert key2 in back_map.contents
        assert back_map.contents[key2] is sass_true
    
    def test_comprehensive_roundtrip(self):
        """Test comprehensive roundtrip conversion with all Node.js features."""
        registry = FunctionRegistry()
        protofier = Protofier(registry)
        
        test_values = [
            # Singletons
            sass_true,
            sass_false,
            sass_null,
            
            # Strings with Node.js features
            SassString("hello", quoted=True),
            SassString("world", quoted=False),
            SassString.empty(quoted=True),
            SassString.empty(quoted=False),
            
            # Numbers with Node.js features
            SassNumber(42.5),
            SassNumber(10, 'px'),
            SassNumber(5, {'numerator_units': ['em'], 'denominator_units': ['s']}),
            
            # Lists with Node.js features
            SassList([SassString("a")], ListSeparator.COMMA, brackets=False),
            SassList([SassNumber(1), SassNumber(2)], ListSeparator.SPACE, brackets=True),
            SassList([sass_true, sass_false], ListSeparator.SLASH),
            
            # Colors with Node.js features
            SassColor(red=255, green=0, blue=0, space='rgb'),
            SassColor(hue=120, saturation=100, lightness=50, space='hsl'),
            SassColor(red=128, green=128, blue=128, alpha=0.5, space='rgb'),
            
            # Maps
            SassMap({SassString("key"): SassNumber(42)}),
        ]
        
        for original in test_values:
            # Convert to protobuf and back
            proto_value = protofier.protofy(original)
            converted = protofier.deprotofy(proto_value)
            
            # Check equality
            assert converted == original, f"Roundtrip failed for {original}"
    
    def test_error_handling(self):
        """Test error handling in Protofier."""
        registry = FunctionRegistry()
        protofier = Protofier(registry)
        
        # Test unknown value type
        class UnknownValue:
            pass
        
        with pytest.raises(CompileException, match="Unknown Value"):
            protofier.protofy(UnknownValue())
        
        # Test empty protobuf value
        empty_proto = proto.Value()
        with pytest.raises(CompileException, match="Value.value is mandatory"):
            protofier.deprotofy(empty_proto)


class TestBackwardCompatibility:
    """Test backward compatibility functions."""
    
    def test_convenience_functions(self):
        """Test convenience functions work with new Protofier."""
        # Test to_proto convenience function
        value = SassString("test")
        proto_value = to_proto(value)
        assert proto_value.string.text == "test"
        
        # Test from_proto convenience function
        converted = from_proto(proto_value)
        assert converted == value
        assert converted.has_quotes == True  # Uses new property
    
    def test_old_property_compatibility(self):
        """Test that old tests still work with property updates."""
        # Old tests might use .quoted instead of .has_quotes
        string_val = SassString("test", quoted=True)
        
        # New property should work
        assert string_val.has_quotes == True
        
        # Constructor parameter should still work
        assert string_val.text == "test"


class TestNodeJSFeatures:
    """Test specific Node.js features that were added."""
    
    def test_sass_string_features(self):
        """Test SassString Node.js features."""
        # Test sass_length property
        string_val = SassString("hello")
        assert string_val.sass_length == 5
        
        # Test empty() static method
        empty = SassString.empty(quoted=False)
        assert empty.text == ""
        assert empty.has_quotes == False
    
    def test_sass_number_features(self):
        """Test SassNumber Node.js features."""
        # Test is_int and as_int
        int_num = SassNumber(42)
        float_num = SassNumber(42.5)
        
        assert int_num.is_int == True
        assert int_num.as_int == 42
        assert float_num.is_int == False
        assert float_num.as_int is None
        
        # Test assert methods
        assert int_num.assert_int() == 42
        assert int_num.assert_in_range(0, 100) == 42
        
        # Test complex units
        complex_num = SassNumber(10, {
            'numerator_units': ['px', 'em'],
            'denominator_units': ['s']
        })
        assert complex_num.numerator_units == ['px', 'em']
        assert complex_num.denominator_units == ['s']
        assert complex_num.has_units == True
    
    def test_sass_color_features(self):
        """Test SassColor Node.js features."""
        color = SassColor(red=255, green=128, blue=0, alpha=0.8, space='rgb')
        
        # Test space property
        assert color.space == 'rgb'
        
        # Test channels_or_null property
        assert color.channels_or_null == [255, 128, 0]
        
        # Test is_channel_missing method
        assert color.is_channel_missing('alpha') == False
        assert color.is_channel_missing('red') == False
        
        # Test color without alpha
        no_alpha = SassColor(red=100, green=100, blue=100, space='rgb')
        assert no_alpha.is_channel_missing('alpha') == True
    
    def test_sass_list_features(self):
        """Test SassList Node.js features."""
        list_val = SassList([SassString("a")], ListSeparator.SPACE, brackets=True)
        
        # Test has_brackets property
        assert list_val.has_brackets == True
        
        # Test separator property
        assert list_val.separator == ' '
