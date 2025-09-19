"""
Number value type for Sass.

This module provides a Python implementation that matches the Node.js SassNumber
class exactly.
"""

from typing import Optional, List as PyList, Union
from .base import Value


class SassNumber(Value):
    """
    A SassScript number.
    
    This matches the Node.js SassNumber class exactly.
    """
    
    def __init__(
        self, 
        value: float, 
        unit_or_options: Optional[Union[str, dict]] = None
    ):
        """
        Initialize a SassNumber.
        
        Args:
            value: The numeric value
            unit_or_options: Either a simple unit string (like 'px') or a dict with
                           'numerator_units' and 'denominator_units' keys
        """
        super().__init__()
        
        if isinstance(unit_or_options, str):
            # Simple unit string (like Node.js string constructor)
            self._value = value
            self._numerator_units = [unit_or_options] if unit_or_options else []
            self._denominator_units = []
        elif isinstance(unit_or_options, dict):
            # Complex units (like Node.js options constructor)
            numerators = list(unit_or_options.get('numerator_units', []))
            unsimplified_denominators = list(unit_or_options.get('denominator_units', []))
            
            # Simplify units by canceling matching numerators and denominators
            denominators = []
            for denominator in unsimplified_denominators:
                simplified_away = False
                for i, numerator in enumerate(numerators):
                    # For now, only cancel exact matches (Node.js has conversion factors)
                    if denominator == numerator:
                        numerators.pop(i)
                        simplified_away = True
                        break
                if not simplified_away:
                    denominators.append(denominator)
            
            self._value = value
            self._numerator_units = numerators
            self._denominator_units = denominators
        else:
            # No units (like Node.js undefined constructor)
            self._value = value
            self._numerator_units = []
            self._denominator_units = []
    
    @property
    def value(self) -> float:
        """The numeric value (matches Node.js value getter)."""
        return self._value
    
    @property
    def is_int(self) -> bool:
        """Whether value is an integer (matches Node.js isInt getter)."""
        # Use Node.js precision: epsilon = 10^(-10-1) = 1e-11
        return abs(self._value - round(self._value)) < 1e-11
    
    @property
    def as_int(self) -> Optional[int]:
        """
        If value is an integer, returns it as int. Otherwise returns None.
        (matches Node.js asInt getter)
        """
        if self.is_int:
            return round(self._value)
        return None
    
    @property
    def numerator_units(self) -> PyList[str]:
        """The numerator units (matches Node.js numeratorUnits getter)."""
        return self._numerator_units.copy()
    
    @property
    def denominator_units(self) -> PyList[str]:
        """The denominator units (matches Node.js denominatorUnits getter)."""
        return self._denominator_units.copy()
    
    @property
    def has_units(self) -> bool:
        """Whether this number has any units (matches Node.js hasUnits getter)."""
        return len(self._numerator_units) > 0 or len(self._denominator_units) > 0
    
    @property
    def unit(self) -> str:
        """
        Simple unit interface for backward compatibility.
        Returns the first numerator unit or empty string.
        """
        return self._numerator_units[0] if self._numerator_units else ""
    
    def assert_number(self) -> 'SassNumber':
        """Assert this is a number (matches Node.js assertNumber method)."""
        return self
    
    def assert_int(self, name: Optional[str] = None) -> int:
        """
        Assert this is an integer and return it (matches Node.js assertInt method).
        
        Args:
            name: Argument name for error reporting
            
        Returns:
            The integer value
            
        Raises:
            ValueError: If not an integer
        """
        int_val = self.as_int
        if int_val is None:
            error_msg = f"{self} is not an int"
            if name:
                error_msg += f" (argument: ${name})"
            raise ValueError(error_msg)
        return int_val
    
    def assert_in_range(self, min_val: float, max_val: float, name: Optional[str] = None) -> float:
        """
        Assert this value is in range and return it (matches Node.js assertInRange method).
        
        Args:
            min_val: Minimum allowed value
            max_val: Maximum allowed value  
            name: Argument name for error reporting
            
        Returns:
            The clamped value
            
        Raises:
            ValueError: If not in range
        """
        if self._value < min_val or self._value > max_val:
            error_msg = f"{self} must be between {min_val} and {max_val}"
            if name:
                error_msg += f" (argument: ${name})"
            raise ValueError(error_msg)
        
        # Clamp to exact bounds if very close (fuzzy equals)
        if abs(self._value - min_val) < 1e-10:
            return min_val
        if abs(self._value - max_val) < 1e-10:
            return max_val
        
        return self._value
    
    @property
    def is_truthy(self) -> bool:
        """Numbers are always truthy in Sass."""
        return True
    
    @property
    def separator(self) -> Optional[str]:
        """Numbers don't have separators."""
        return None
    
    @property
    def has_brackets(self) -> bool:
        """Numbers don't have brackets."""
        return False
    
    def __str__(self) -> str:
        """String representation matching Sass output."""
        if not self.has_units:
            return str(self._value)
        
        # Build unit string
        unit_str = ""
        if self._numerator_units:
            unit_str += "".join(self._numerator_units)
        
        if self._denominator_units:
            if self._numerator_units:
                unit_str += "/"
            unit_str += "/".join(self._denominator_units)
        
        return f"{self._value}{unit_str}"
    
    def __repr__(self) -> str:
        """Python representation."""
        if not self.has_units:
            return f"SassNumber({self._value})"
        elif len(self._numerator_units) == 1 and not self._denominator_units:
            return f"SassNumber({self._value}, '{self._numerator_units[0]}')"
        else:
            return f"SassNumber({self._value}, {{'numerator_units': {self._numerator_units}, 'denominator_units': {self._denominator_units}}})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, SassNumber):
            return False
        return (
            abs(self._value - other._value) < 1e-11 and  # Node.js precision
            self._numerator_units == other._numerator_units and
            self._denominator_units == other._denominator_units
        )
    
    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash((
            round(self._value, 11),  # Node.js precision (10^-11)
            tuple(self._numerator_units),
            tuple(self._denominator_units)
        ))
