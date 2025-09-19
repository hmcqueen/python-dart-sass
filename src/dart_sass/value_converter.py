"""
Value conversion between Python Sass values and protobuf messages.

This module provides a Python implementation that matches the Node.js Protofier
class exactly, using modern Python match-case syntax.
"""

from typing import Any, List as PyList, Dict as PyDict, Optional, TYPE_CHECKING
from .vendor import embedded_sass_pb2 as proto
from .value.base import Value
from .value.boolean import SassBoolean, sass_true, sass_false
from .value.null import SassNull, sass_null
from .value.string import SassString
from .value.number import SassNumber
from .value.list import SassList, ListSeparator
from .value.map import SassMap
from .value.color import SassColor
from .value.function import SassFunction
from .value.mixin import SassMixin
from .value.argument_list import SassArgumentList
from .value.calculations import SassCalculation, CalculationOperation, CalculationInterpolation
from .exception import CompileException

if TYPE_CHECKING:
    from .function_registry import FunctionRegistry


class Protofier:
    """
    A class that converts Value objects into protobufs.
    
    This matches the Node.js Protofier class exactly. A given Protofier instance 
    is valid only within the scope of a single custom function call.
    """
    
    def __init__(self, functions: 'FunctionRegistry'):
        """
        Initialize the protofier.
        
        Args:
            functions: The registry of custom functions that can be invoked by the compiler.
        """
        self.functions = functions
        self._argument_lists: PyList[SassArgumentList] = []
    
    @property
    def accessed_argument_lists(self) -> PyList[int]:
        """
        Returns IDs of all argument lists whose keywords have been accessed.
        """
        return [
            arg_list.id for arg_list in self._argument_lists 
            if hasattr(arg_list, 'keywords_accessed') and arg_list.keywords_accessed
        ]
    
    def protofy(self, value: Value) -> proto.Value:
        """
        Convert a Python Sass value to its protocol buffer representation.
        
        Args:
            value: The Python Sass value to convert
            
        Returns:
            Protobuf Value message
        """
        proto_value = proto.Value()
        
        match value:
            case SassString():
                proto_value.string.text = value.text
                proto_value.string.quoted = value.has_quotes
                
            case SassNumber():
                proto_value.number.value = value.value
                # Use the proper numerator/denominator units interface (like Node.js)
                proto_value.number.numerators.extend(value.numerator_units)
                proto_value.number.denominators.extend(value.denominator_units)
                    
            case SassColor():
                channels = value.channels_or_null
                proto_value.color.space = value.space
                
                if len(channels) >= 1 and channels[0] is not None:
                    proto_value.color.channel1 = channels[0]
                if len(channels) >= 2 and channels[1] is not None:
                    proto_value.color.channel2 = channels[1]
                if len(channels) >= 3 and channels[2] is not None:
                    proto_value.color.channel3 = channels[2]
                    
                # Handle alpha channel (like Node.js)
                if not value.is_channel_missing('alpha'):
                    proto_value.color.alpha = value.alpha
                    
            case SassList():
                proto_value.list.separator = self._protofy_separator(value.separator)
                proto_value.list.has_brackets = value.has_brackets
                
                for element in value.contents:
                    proto_value.list.contents.append(self.protofy(element))
                    
            case SassArgumentList():
                if hasattr(value, 'compile_context') and value.compile_context == self.functions.compile_context:
                    proto_value.argument_list.id = getattr(value, 'id', 0)
                else:
                    proto_value.argument_list.separator = self._protofy_separator(value.separator)
                    
                    for element in value.contents:
                        proto_value.argument_list.contents.append(self.protofy(element))
                    
                    if hasattr(value, 'keywords_internal'):
                        for key, map_value in value.keywords_internal.items():
                            proto_value.argument_list.keywords[key].CopyFrom(self.protofy(map_value))
                            
            case SassMap():
                for key, map_value in value.contents.items():
                    entry = proto_value.map.entries.add()
                    entry.key.CopyFrom(self.protofy(key))
                    entry.value.CopyFrom(self.protofy(map_value))
                    
            case SassFunction():
                if hasattr(value, 'id') and value.id is not None:
                    if hasattr(value, 'compile_context') and value.compile_context != self.functions.compile_context:
                        raise CompileException(f"Value {value} does not belong to this compilation")
                    proto_value.compiler_function.id = value.id
                else:
                    if hasattr(value, 'callback') and value.callback:
                        function_id = self.functions.register(value.callback)
                        proto_value.host_function.id = function_id
                        proto_value.host_function.signature = getattr(value, 'signature', 'unknown()')
                    else:
                        raise CompileException("Host function missing callback")
                        
            case SassMixin():
                if hasattr(value, 'compile_context') and value.compile_context != self.functions.compile_context:
                    raise CompileException(f"Value {value} does not belong to this compilation")
                proto_value.compiler_mixin.id = getattr(value, 'id', 0)
                
            case SassCalculation():
                proto_value.calculation.name = value.name
                for arg in value.arguments:
                    proto_value.calculation.arguments.append(self._protofy_calculation_value(arg))
                    
            case _ if value is sass_true:
                proto_value.singleton = proto.SingletonValue.TRUE
                
            case _ if value is sass_false:
                proto_value.singleton = proto.SingletonValue.FALSE
                
            case _ if value is sass_null:
                proto_value.singleton = proto.SingletonValue.NULL
                
            case _:
                raise CompileException(f"Unknown Value {value}")
        
        return proto_value
    
    def deprotofy(self, proto_value: proto.Value) -> Value:
        """
        Convert a protobuf Value to its Python Sass representation.
        """
        match True:
            case _ if proto_value.HasField('string'):
                string_val = proto_value.string
                if len(string_val.text) == 0:
                    return SassString.empty(quoted=string_val.quoted)
                return SassString(string_val.text, quoted=string_val.quoted)
                
            case _ if proto_value.HasField('number'):
                return self._deprotofy_number(proto_value.number)
                
            case _ if proto_value.HasField('color'):
                return self._deprotofy_color(proto_value.color)
                
            case _ if proto_value.HasField('list'):
                list_val = proto_value.list
                separator = self._deprotofy_separator(list_val.separator)
                
                if separator is None and len(list_val.contents) > 1:
                    raise CompileException(
                        f"Value.List can't have an undecided separator because it has {len(list_val.contents)} elements"
                    )
                
                contents = [self.deprotofy(element) for element in list_val.contents]
                return SassList(contents, separator=separator, brackets=list_val.has_brackets)
                
            case _ if proto_value.HasField('argument_list'):
                list_val = proto_value.argument_list
                separator = self._deprotofy_separator(list_val.separator)
                
                if separator is None and len(list_val.contents) > 1:
                    raise CompileException(
                        f"Value.List can't have an undecided separator because it has {len(list_val.contents)} elements"
                    )
                
                contents = [self.deprotofy(element) for element in list_val.contents]
                keywords = {key: self.deprotofy(value) for key, value in list_val.keywords.items()}
                
                result = SassArgumentList(
                    contents, 
                    keywords=keywords,
                    separator=separator,
                    id=getattr(list_val, 'id', None),
                    compile_context=self.functions.compile_context
                )
                self._argument_lists.append(result)
                return result
                
            case _ if proto_value.HasField('map'):
                entries = {}
                for entry in proto_value.map.entries:
                    if not entry.HasField('key'):
                        raise CompileException('Value.Map.Entry.key is mandatory')
                    if not entry.HasField('value'):
                        raise CompileException('Value.Map.Entry.value is mandatory')
                        
                    key = self.deprotofy(entry.key)
                    value = self.deprotofy(entry.value)
                    entries[key] = value
                return SassMap(entries)
                
            case _ if proto_value.HasField('compiler_function'):
                return SassFunction(
                    id=proto_value.compiler_function.id,
                    compile_context=self.functions.compile_context
                )
                
            case _ if proto_value.HasField('host_function'):
                raise CompileException('The compiler may not send Value.host_function.')
                
            case _ if proto_value.HasField('compiler_mixin'):
                return SassMixin(
                    id=proto_value.compiler_mixin.id,
                    compile_context=self.functions.compile_context
                )
                
            case _ if proto_value.HasField('calculation'):
                return self._deprotofy_calculation(proto_value.calculation)
                
            case _ if proto_value.HasField('singleton'):
                match proto_value.singleton:
                    case proto.SingletonValue.TRUE:
                        return sass_true
                    case proto.SingletonValue.FALSE:
                        return sass_false
                    case proto.SingletonValue.NULL:
                        return sass_null
                    case _:
                        raise CompileException(f"Unknown singleton value: {proto_value.singleton}")
                        
            case _:
                raise CompileException('Value.value is mandatory')
    
    def _protofy_separator(self, separator) -> proto.ListSeparator:
        """Convert separator to its protocol buffer representation."""
        sep_str = separator.value if hasattr(separator, 'value') else str(separator)
        
        match sep_str:
            case 'comma' | ',':
                return proto.ListSeparator.COMMA
            case 'space' | ' ':
                return proto.ListSeparator.SPACE
            case 'slash' | '/':
                return proto.ListSeparator.SLASH
            case 'undecided' | None:
                return proto.ListSeparator.UNDECIDED
            case _:
                raise CompileException(f"Unknown ListSeparator {separator}")
    
    def _deprotofy_separator(self, separator: proto.ListSeparator):
        """Convert separator to its Python representation."""
        match separator:
            case proto.ListSeparator.COMMA:
                return ListSeparator.COMMA
            case proto.ListSeparator.SPACE:
                return ListSeparator.SPACE
            case proto.ListSeparator.SLASH:
                return ListSeparator.SLASH
            case proto.ListSeparator.UNDECIDED:
                return ListSeparator.UNDECIDED
            case _:
                raise CompileException(f"Unknown separator {separator}")
    
    def _deprotofy_number(self, number: proto.Value.Number) -> SassNumber:
        """Convert number to its Python representation."""
        return SassNumber(
            number.value,
            {
                'numerator_units': list(number.numerators),
                'denominator_units': list(number.denominators)
            }
        )
    
    def _deprotofy_color(self, color: proto.Value.Color) -> SassColor:
        """Convert color to its Python representation."""
        channel1 = color.channel1 if color.HasField('channel1') else None
        channel2 = color.channel2 if color.HasField('channel2') else None  
        channel3 = color.channel3 if color.HasField('channel3') else None
        alpha = color.alpha if color.HasField('alpha') else None
        space = color.space
        
        match space.lower():
            case 'rgb' | 'srgb' | 'srgb-linear' | 'display-p3' | 'a98-rgb' | 'prophoto-rgb' | 'rec2020':
                return SassColor(red=channel1, green=channel2, blue=channel3, alpha=alpha, space=space)
            case 'hsl':
                return SassColor(hue=channel1, saturation=channel2, lightness=channel3, alpha=alpha, space=space)
            case 'hwb':
                return SassColor(hue=channel1, whiteness=channel2, blackness=channel3, alpha=alpha, space=space)
            case 'lab' | 'oklab':
                return SassColor(lightness=channel1, a=channel2, b=channel3, alpha=alpha, space=space)
            case 'lch' | 'oklch':
                return SassColor(lightness=channel1, chroma=channel2, hue=channel3, alpha=alpha, space=space)
            case 'xyz' | 'xyz-d65' | 'xyz-d50':
                return SassColor(x=channel1, y=channel2, z=channel3, alpha=alpha, space=space)
            case _:
                raise CompileException(f'Unknown color space "{space}".')
    
    def _protofy_calculation_value(self, value) -> proto.Value.Calculation.CalculationValue:
        """Convert a CalculationValue to its protobuf representation."""
        proto_calc_value = proto.Value.Calculation.CalculationValue()
        
        match value:
            case SassCalculation():
                proto_calc_value.calculation.CopyFrom(self._protofy_calculation(value))
            case CalculationOperation():
                proto_calc_value.operation.operator = self._protofy_calculation_operator(value.operator)
                proto_calc_value.operation.left.CopyFrom(self._protofy_calculation_value(value.left))
                proto_calc_value.operation.right.CopyFrom(self._protofy_calculation_value(value.right))
            case CalculationInterpolation():
                proto_calc_value.interpolation = value.value
            case SassString():
                proto_calc_value.string = value.text
            case SassNumber():
                proto_calc_value.number.CopyFrom(self._protofy_number(value))
            case _:
                raise CompileException(f"Unknown CalculationValue {value}")
                
        return proto_calc_value
    
    def _protofy_calculation(self, calculation: SassCalculation) -> proto.Value.Calculation:
        """Convert calculation to its protobuf representation."""
        proto_calc = proto.Value.Calculation()
        proto_calc.name = calculation.name
        for arg in calculation.arguments:
            proto_calc.arguments.append(self._protofy_calculation_value(arg))
        return proto_calc
    
    def _protofy_calculation_operator(self, operator) -> proto.CalculationOperator:
        """Convert operator to its protobuf representation."""
        match operator:
            case '+':
                return proto.CalculationOperator.PLUS
            case '-':
                return proto.CalculationOperator.MINUS
            case '*':
                return proto.CalculationOperator.TIMES
            case '/':
                return proto.CalculationOperator.DIVIDE
            case _:
                raise CompileException(f"Unknown CalculationOperator {operator}")
    
    def _deprotofy_calculation(self, calculation: proto.Value.Calculation) -> SassCalculation:
        """Convert calculation to its Python representation."""
        match calculation.name:
            case 'calc':
                if len(calculation.arguments) != 1:
                    raise CompileException('Value.Calculation.arguments must have exactly one argument for calc().')
                return SassCalculation.calc(self._deprotofy_calculation_value(calculation.arguments[0]))
                
            case 'clamp':
                if len(calculation.arguments) == 0 or len(calculation.arguments) > 3:
                    raise CompileException('Value.Calculation.arguments must have 1 to 3 arguments for clamp().')
                args = [self._deprotofy_calculation_value(arg) for arg in calculation.arguments]
                return SassCalculation.clamp(*args)
                
            case 'min':
                if len(calculation.arguments) == 0:
                    raise CompileException('Value.Calculation.arguments must have at least 1 argument for min().')
                args = [self._deprotofy_calculation_value(arg) for arg in calculation.arguments]
                return SassCalculation.min(args)
                
            case 'max':
                if len(calculation.arguments) == 0:
                    raise CompileException('Value.Calculation.arguments must have at least 1 argument for max().')
                args = [self._deprotofy_calculation_value(arg) for arg in calculation.arguments]
                return SassCalculation.max(args)
                
            case _:
                raise CompileException(f'Value.Calculation.name "{calculation.name}" is not a recognized calculation type.')
    
    def _deprotofy_calculation_value(self, value: proto.Value.Calculation.CalculationValue):
        """Convert CalculationValue to its Python representation."""
        match True:
            case _ if value.HasField('number'):
                return self._deprotofy_number(value.number)
            case _ if value.HasField('calculation'):
                return self._deprotofy_calculation(value.calculation)
            case _ if value.HasField('string'):
                return SassString(value.string, quoted=False)
            case _ if value.HasField('operation'):
                op = value.operation
                return CalculationOperation(
                    self._deprotofy_calculation_operator(op.operator),
                    self._deprotofy_calculation_value(op.left),
                    self._deprotofy_calculation_value(op.right)
                )
            case _ if value.HasField('interpolation'):
                return CalculationInterpolation(value.interpolation)
            case _:
                raise CompileException('Calculation.CalculationValue.value is mandatory')
    
    def _deprotofy_calculation_operator(self, operator: proto.CalculationOperator):
        """Convert operator to its Python representation."""
        match operator:
            case proto.CalculationOperator.PLUS:
                return '+'
            case proto.CalculationOperator.MINUS:
                return '-'
            case proto.CalculationOperator.TIMES:
                return '*'
            case proto.CalculationOperator.DIVIDE:
                return '/'
            case _:
                raise CompileException(f"Unknown CalculationOperator {operator}")
    
    def _protofy_number(self, number: SassNumber) -> proto.Value.Number:
        """Convert number to its protobuf representation."""
        proto_number = proto.Value.Number()
        proto_number.value = number.value
        
        if hasattr(number, 'numerator_units'):
            proto_number.numerators.extend(number.numerator_units)
        elif number.unit:
            proto_number.numerators.append(number.unit)
        
        if hasattr(number, 'denominator_units'):
            proto_number.denominators.extend(number.denominator_units)
            
        return proto_number


# Convenience functions for backward compatibility
def to_proto(value: Value) -> proto.Value:
    """Convert a Python Sass value to protobuf."""
    from .function_registry import FunctionRegistry
    protofier = Protofier(FunctionRegistry())
    return protofier.protofy(value)


def from_proto(proto_value: proto.Value) -> Value:
    """Convert a protobuf value to Python Sass value."""
    from .function_registry import FunctionRegistry
    protofier = Protofier(FunctionRegistry())
    return protofier.deprotofy(proto_value)


def to_proto_list(values: PyList[Value]) -> PyList[proto.Value]:
    """Convert a list of Python Sass values to protobuf."""
    from .function_registry import FunctionRegistry
    protofier = Protofier(FunctionRegistry())
    return [protofier.protofy(value) for value in values]


def from_proto_list(proto_values: PyList[proto.Value]) -> PyList[Value]:
    """Convert a list of protobuf values to Python Sass values."""
    from .function_registry import FunctionRegistry
    protofier = Protofier(FunctionRegistry())
    return [protofier.deprotofy(proto_value) for proto_value in proto_values]
