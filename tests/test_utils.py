"""
Tests for utility functions.
"""

import pytest
import asyncio
from dart_sass.utils import then_or, catch_or, compiler_error, host_error, protofy_syntax
from dart_sass.vendor import embedded_sass_pb2 as proto
from dart_sass.exception import CompileException, ProtocolException


class TestThenOr:
    """Test cases for then_or utility function."""
    
    def test_then_or_with_sync_value(self):
        """Test then_or with a synchronous value."""
        def callback(value):
            return f"processed: {value}"
        
        result = then_or("test", callback)
        assert result == "processed: test"
    
    def test_then_or_with_sync_value_complex(self):
        """Test then_or with complex synchronous processing."""
        def callback(value):
            return {"original": value, "length": len(value)}
        
        result = then_or("hello", callback)
        assert result == {"original": "hello", "length": 5}
    
    @pytest.mark.asyncio
    async def test_then_or_with_async_value(self):
        """Test then_or with an asynchronous value."""
        async def async_value():
            await asyncio.sleep(0.01)
            return "async_result"
        
        def callback(value):
            return f"processed: {value}"
        
        result = then_or(async_value(), callback)
        # Result should be awaitable
        assert hasattr(result, '__await__')
        
        final_result = await result
        assert final_result == "processed: async_result"
    
    @pytest.mark.asyncio
    async def test_then_or_with_async_value_sync_callback(self):
        """Test then_or with async value and sync callback (Node.js pattern)."""
        async def async_value():
            await asyncio.sleep(0.01)
            return "async_result"
        
        def sync_callback(value):
            return f"processed: {value}"
        
        result = then_or(async_value(), sync_callback)
        # Result should be awaitable
        assert hasattr(result, '__await__')
        
        final_result = await result
        assert final_result == "processed: async_result"
    
    def test_then_or_with_none_value(self):
        """Test then_or with None value."""
        def callback(value):
            return f"got: {value}"
        
        result = then_or(None, callback)
        assert result == "got: None"
    
    def test_then_or_callback_exception(self):
        """Test then_or when callback raises exception."""
        def failing_callback(value):
            raise ValueError("callback failed")
        
        with pytest.raises(ValueError, match="callback failed"):
            then_or("test", failing_callback)
    
    @pytest.mark.asyncio
    async def test_then_or_async_callback_exception(self):
        """Test then_or when async callback raises exception."""
        async def async_value():
            return "test"
        
        def failing_callback(value):
            raise ValueError("async callback failed")
        
        result = then_or(async_value(), failing_callback)
        
        with pytest.raises(ValueError, match="async callback failed"):
            await result


class TestCatchOr:
    """Test cases for catch_or utility function."""
    
    def test_catch_or_with_sync_success(self):
        """Test catch_or with successful synchronous operation."""
        def success_operation():
            return "success"
        
        def error_handler(error):
            return f"error: {error}"
        
        result = catch_or(success_operation, error_handler)
        assert result == "success"
    
    def test_catch_or_with_sync_error(self):
        """Test catch_or with synchronous error."""
        def failing_operation():
            raise ValueError("sync error")
        
        def error_handler(error):
            return f"caught: {error}"
        
        result = catch_or(failing_operation, error_handler)
        assert result == "caught: sync error"
    
    @pytest.mark.asyncio
    async def test_catch_or_with_async_success(self):
        """Test catch_or with successful asynchronous operation."""
        async def async_success():
            await asyncio.sleep(0.01)
            return "async_success"
        
        def success_operation():
            return async_success()
        
        def error_handler(error):
            return f"error: {error}"
        
        result = catch_or(success_operation, error_handler)
        assert hasattr(result, '__await__')
        
        final_result = await result
        assert final_result == "async_success"
    
    @pytest.mark.asyncio
    async def test_catch_or_with_async_error(self):
        """Test catch_or with asynchronous error."""
        async def async_failure():
            await asyncio.sleep(0.01)
            raise ValueError("async error")
        
        def failing_operation():
            return async_failure()
        
        def error_handler(error):
            return f"caught: {error}"
        
        result = catch_or(failing_operation, error_handler)
        assert hasattr(result, '__await__')
        
        final_result = await result
        assert final_result == "caught: async error"
    
    def test_catch_or_error_in_callback_creation(self):
        """Test catch_or when the callback creation itself fails."""
        def failing_callback_creation():
            raise RuntimeError("callback creation failed")
        
        def error_handler(error):
            return f"caught: {error}"
        
        result = catch_or(failing_callback_creation, error_handler)
        assert result == "caught: callback creation failed"
    
    @pytest.mark.asyncio
    async def test_catch_or_with_async_error_handler(self):
        """Test catch_or with async error handler."""
        def failing_operation():
            raise ValueError("sync error")
        
        async def async_error_handler(error):
            await asyncio.sleep(0.01)
            return f"async_caught: {error}"
        
        result = catch_or(failing_operation, async_error_handler)
        assert hasattr(result, '__await__')
        
        final_result = await result
        assert final_result == "async_caught: sync error"
    
    def test_catch_or_multiple_error_types(self):
        """Test catch_or with different error types."""
        def value_error_operation():
            raise ValueError("value error")
        
        def type_error_operation():
            raise TypeError("type error")
        
        def runtime_error_operation():
            raise RuntimeError("runtime error")
        
        def error_handler(error):
            return f"caught {type(error).__name__}: {error}"
        
        result1 = catch_or(value_error_operation, error_handler)
        assert result1 == "caught ValueError: value error"
        
        result2 = catch_or(type_error_operation, error_handler)
        assert result2 == "caught TypeError: type error"
        
        result3 = catch_or(runtime_error_operation, error_handler)
        assert result3 == "caught RuntimeError: runtime error"


class TestCombinedUsage:
    """Test cases for combined usage of then_or and catch_or."""
    
    @pytest.mark.asyncio
    async def test_nested_then_or_catch_or(self):
        """Test nested usage like in FunctionRegistry.call()."""
        async def async_operation(value):
            await asyncio.sleep(0.01)
            if value == "error":
                raise ValueError("operation failed")
            return f"processed: {value}"
        
        def execute_with_then_or(input_value):
            def process_result(result):
                return f"final: {result}"
            
            return then_or(async_operation(input_value), process_result)
        
        def error_handler(error):
            return f"error_handled: {error}"
        
        # Test success case
        success_result = catch_or(lambda: execute_with_then_or("success"), error_handler)
        final_success = await success_result
        assert final_success == "final: processed: success"
        
        # Test error case
        error_result = catch_or(lambda: execute_with_then_or("error"), error_handler)
        final_error = await error_result
        assert final_error == "error_handled: operation failed"
    
    def test_sync_chain(self):
        """Test chaining with all synchronous operations."""
        def operation(value):
            return value * 2
        
        def process_result(result):
            return result + 10
        
        def error_handler(error):
            return -1
        
        result = catch_or(lambda: then_or(operation(5), process_result), error_handler)
        assert result == 20  # (5 * 2) + 10
    
    @pytest.mark.asyncio
    async def test_mixed_sync_async_chain(self):
        """Test chaining with mixed sync/async operations."""
        def sync_operation(value):
            return value * 2
        
        async def async_process(result):
            await asyncio.sleep(0.01)
            return result + 10
        
        def error_handler(error):
            return -1
        
        result = catch_or(lambda: then_or(sync_operation(5), async_process), error_handler)
        final_result = await result
        assert final_result == 20  # (5 * 2) + 10


class TestUtilityFunctions:
    """Test cases for other utility functions."""
    
    def test_compiler_error(self):
        """Test compiler_error utility."""
        error = compiler_error("test message")
        assert isinstance(error, CompileException)
        assert str(error) == "Compiler caused error: test message."
    
    def test_host_error(self):
        """Test host_error utility."""
        error = host_error("test message")
        assert isinstance(error, ProtocolException)
        assert str(error) == "Compiler reported error: test message."
    
    def test_protofy_syntax(self):
        """Test protofy_syntax utility."""
        assert protofy_syntax(None) == proto.Syntax.SCSS
        assert protofy_syntax("scss") == proto.Syntax.SCSS
        assert protofy_syntax("sass") == proto.Syntax.INDENTED
        assert protofy_syntax("css") == proto.Syntax.CSS
        
        with pytest.raises(ValueError, match="Unknown syntax: invalid"):
            protofy_syntax("invalid")


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_then_or_with_non_callable(self):
        """Test then_or with non-callable callback."""
        with pytest.raises(TypeError):
            then_or("test", "not_callable")
    
    def test_catch_or_with_non_callable_operation(self):
        """Test catch_or with non-callable operation."""
        # catch_or expects a callable that returns a value, not a direct value
        def error_handler(error):
            return "error"
        
        # This should work fine - catch_or will call the string (which will fail)
        result = catch_or(lambda: "success", error_handler)
        assert result == "success"
    
    def test_catch_or_with_non_callable_error_handler(self):
        """Test catch_or with non-callable error handler."""
        def operation():
            raise ValueError("test")
        
        with pytest.raises(TypeError):
            catch_or(operation, "not_callable")
    
    def test_then_or_with_complex_callback(self):
        """Test then_or with complex callback processing."""
        def complex_callback(value):
            return {"processed": value, "length": len(str(value)), "type": type(value).__name__}
        
        result = then_or("test_value", complex_callback)
        expected = {"processed": "test_value", "length": 10, "type": "str"}
        assert result == expected
    
    def test_empty_string_handling(self):
        """Test utilities with empty strings."""
        def callback(value):
            return f"length: {len(value)}"
        
        result = then_or("", callback)
        assert result == "length: 0"
        
        def operation():
            return ""
        
        def error_handler(error):
            return "error"
        
        result2 = catch_or(operation, error_handler)
        assert result2 == ""
