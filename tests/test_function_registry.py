"""
Tests for function registry.
"""

import pytest
from dart_sass.function_registry import FunctionRegistry
from dart_sass.value.string import SassString
from dart_sass.value.number import SassNumber
from dart_sass.exception import CompileException


class TestFunctionRegistry:
    """Test cases for function registry."""
    
    def test_constructor_with_functions(self):
        """Test constructor with functions (Node.js pattern)."""
        def test_func(args):
            return SassString("test")
        
        # Use Node.js constructor pattern
        registry = FunctionRegistry({"test()": test_func})
        
        # Test that function is stored by name (Node.js behavior)
        assert "test" in registry._functions_by_name
    
    def test_constructor_validation(self):
        """Test constructor validation (Node.js pattern)."""
        def test_func(args):
            return SassString("test")
        
        # Test Node.js constructor validation
        with pytest.raises(ValueError, match='options.functions: "invalid" is missing "\\("'):
            FunctionRegistry({"invalid": test_func})
    
    def test_register_method(self):
        """Test register method (Node.js pattern)."""
        def test_func(args):
            return SassString("test")
        
        registry = FunctionRegistry()
        
        # Test Node.js register method
        id1 = registry.register(test_func)
        id2 = registry.register(test_func)  # Should return same ID
        
        assert id1 == id2  # putIfAbsent behavior
        assert registry._functions_by_id[id1] == test_func
    
    def test_function_name_parsing(self):
        """Test function name parsing (Node.js constructor logic)."""
        def test_func(args):
            return SassString("test")
        
        # Test Node.js constructor parsing logic
        registry = FunctionRegistry({
            "simple()": test_func,
            "with-args($a, $b)": test_func,
            "  spaced  ($x)": test_func
        })
        
        # Verify names are parsed correctly (Node.js behavior)
        assert "simple" in registry._functions_by_name
        assert "with-args" in registry._functions_by_name
        assert "  spaced  " in registry._functions_by_name  # Node.js doesn't trim
    
    def test_empty_constructor(self):
        """Test empty constructor (Node.js pattern)."""
        registry = FunctionRegistry()
        
        assert len(registry._functions_by_name) == 0
        assert len(registry._functions_by_id) == 0
        assert registry._next_id == 0
    
    def test_none_constructor(self):
        """Test constructor with None (Node.js pattern)."""
        registry = FunctionRegistry(None)
        
        assert len(registry._functions_by_name) == 0
        assert len(registry._functions_by_id) == 0
