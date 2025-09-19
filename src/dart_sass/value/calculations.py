"""
Calculation value types for Sass.
"""

from enum import Enum
from typing import Optional, Union, List
from .base import Value


class CalculationOperator(Enum):
    """Operators for Sass calculations."""
    PLUS = "+"
    MINUS = "-"
    TIMES = "*"
    DIVIDE = "/"


class CalculationOperation:
    """
    A calculation operation.
    
    Represents an operation like `1px + 2px` within a calc() expression.
    """
    
    def __init__(self, operator: CalculationOperator, left: "CalculationValue", right: "CalculationValue"):
        """
        Initialize a CalculationOperation.
        
        Args:
            operator: The operation operator
            left: The left operand
            right: The right operand
        """
        self.operator = operator
        self.left = left
        self.right = right
    
    def __eq__(self, other: object) -> bool:
        """Check if this operation equals another operation."""
        if not isinstance(other, CalculationOperation):
            return False
        return (
            self.operator == other.operator and
            self.left == other.left and
            self.right == other.right
        )
    
    def __hash__(self) -> int:
        """Return the hash of this operation."""
        return hash((self.operator, self.left, self.right))
    
    def __str__(self) -> str:
        """Return the string representation of this operation."""
        return f"{self.left} {self.operator.value} {self.right}"
    
    def __repr__(self) -> str:
        """Return the debug representation of this operation."""
        return f"CalculationOperation({self.operator!r}, {self.left!r}, {self.right!r})"


class CalculationInterpolation:
    """
    A calculation interpolation.
    
    Represents an interpolated value like `#{$var}` within a calc() expression.
    """
    
    def __init__(self, value: str):
        """
        Initialize a CalculationInterpolation.
        
        Args:
            value: The interpolated string value
        """
        self.value = value
    
    def __eq__(self, other: object) -> bool:
        """Check if this interpolation equals another interpolation."""
        if not isinstance(other, CalculationInterpolation):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Return the hash of this interpolation."""
        return hash(self.value)
    
    def __str__(self) -> str:
        """Return the string representation of this interpolation."""
        return self.value
    
    def __repr__(self) -> str:
        """Return the debug representation of this interpolation."""
        return f"CalculationInterpolation({self.value!r})"


# Type alias for calculation values
CalculationValue = Union[Value, CalculationOperation, CalculationInterpolation]


class SassCalculation(Value):
    """
    A Sass calculation value.
    
    Represents a CSS calc() expression or similar mathematical function.
    """
    
    def __init__(self, name: str, arguments: List[CalculationValue]):
        """
        Initialize a SassCalculation.
        
        Args:
            name: The calculation function name (e.g., "calc", "min", "max")
            arguments: The calculation arguments
        """
        self._name = name
        self._arguments = list(arguments)
    
    @property
    def name(self) -> str:
        """The calculation function name."""
        return self._name
    
    @property
    def arguments(self) -> List[CalculationValue]:
        """The calculation arguments."""
        return self._arguments.copy()
    
    @property
    def is_truthy(self) -> bool:
        """Whether this value is truthy in Sass."""
        return True
    
    @property
    def separator(self) -> Optional[str]:
        """The separator for this value if it's a list, None otherwise."""
        return None
    
    @property
    def has_brackets(self) -> bool:
        """Whether this value has brackets if it's a list, False otherwise."""
        return False
    
    @classmethod
    def calc(cls, argument: CalculationValue) -> "SassCalculation":
        """Create a calc() calculation."""
        return cls("calc", [argument])
    
    @classmethod
    def min(cls, arguments: List[CalculationValue]) -> "SassCalculation":
        """Create a min() calculation."""
        return cls("min", arguments)
    
    @classmethod
    def max(cls, arguments: List[CalculationValue]) -> "SassCalculation":
        """Create a max() calculation."""
        return cls("max", arguments)
    
    @classmethod
    def clamp(cls, min_val: CalculationValue, val: CalculationValue, max_val: CalculationValue) -> "SassCalculation":
        """Create a clamp() calculation."""
        return cls("clamp", [min_val, val, max_val])
    
    def __eq__(self, other: object) -> bool:
        """Check if this value equals another value."""
        if not isinstance(other, SassCalculation):
            return False
        return self._name == other._name and self._arguments == other._arguments
    
    def __hash__(self) -> int:
        """Return the hash of this value."""
        return hash((self._name, tuple(self._arguments)))
    
    def __str__(self) -> str:
        """Return the string representation of this value."""
        args_str = ", ".join(str(arg) for arg in self._arguments)
        return f"{self._name}({args_str})"
    
    def __repr__(self) -> str:
        """Return the debug representation of this value."""
        return f"SassCalculation({self._name!r}, {self._arguments!r})"
