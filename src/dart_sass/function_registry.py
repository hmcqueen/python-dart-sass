"""
Function registry for custom Sass functions.

This module provides a Python implementation that matches the Node.js reference
implementation exactly.
"""

from typing import Dict, Callable, List, Optional, Any
from .value.base import Value
from .vendor import embedded_sass_pb2 as proto
from .exception import CompileException


# Type alias for Sass function callbacks
# Matches Node.js: receives list of Values, returns Value
SassFunction = Callable[[List[Value]], Value]


class FunctionRegistry:
    """
    Tracks functions that are defined on the host so that the compiler can execute them.
    
    This implementation matches the Node.js reference implementation exactly.
    """
    
    def __init__(self, functions_by_signature: Optional[Dict[str, SassFunction]] = None):
        """
        Initialize the function registry.
        
        Args:
            functions_by_signature: Optional dict of signature -> function mappings
                                  (matches Node.js constructor exactly)
        """
        # The globally unique identifier of the current compilation used for tracking
        # the ownership of CompilerFunction and CompilerMixin objects (like Node.js)
        self.compile_context = object()  # Python equivalent of Symbol()
        
        # Store functions by name for efficient lookup (like Node.js functionsByName)
        self._functions_by_name: Dict[str, SassFunction] = {}
        
        # Store functions by ID for protobuf calls (like Node.js functionsById)
        self._functions_by_id: Dict[int, SassFunction] = {}
        self._ids_by_function: Dict[SassFunction, int] = {}
        
        # The next ID to use for a function (like Node.js)
        self._next_id = 0
        
        # Register functions from constructor parameter (EXACTLY like Node.js)
        if functions_by_signature:
            for signature, function in functions_by_signature.items():
                # Exactly like Node.js: const openParen = signature.indexOf('(');
                open_paren = signature.find('(')
                if open_paren == -1:
                    # Exactly like Node.js error message
                    raise ValueError(f'options.functions: "{signature}" is missing "("')
                
                # Exactly like Node.js: this.functionsByName.set(signature.substring(0, openParen), fn);
                function_name = signature[:open_paren]
                self._functions_by_name[function_name] = function
    
    def register(self, function: SassFunction) -> int:
        """
        Register a function and return its ID (exactly like Node.js register method).
        
        This matches the Node.js signature: register(fn: CustomFunction<sync>): number
        
        Args:
            function: The function to register
            
        Returns:
            The unique ID assigned to this function
        """
        # Implement putIfAbsent pattern like Node.js utils.putIfAbsent
        if function in self._ids_by_function:
            return self._ids_by_function[function]
        
        # Assign new ID (like Node.js: const id = this.id; this.id += 1;)
        function_id = self._next_id
        self._next_id += 1
        self._functions_by_id[function_id] = function
        self._ids_by_function[function] = function_id
        return function_id
    
    def call(self, request: proto.OutboundMessage.FunctionCallRequest) -> proto.InboundMessage.FunctionCallResponse:
        """
        Handle a function call request and return protobuf response.
        
        This method matches the Node.js FunctionRegistry.call() method exactly,
        including support for both sync and async functions using catchOr/thenOr pattern.
        
        Args:
            request: OutboundMessage_FunctionCallRequest from the Sass compiler
            
        Returns:
            InboundMessage_FunctionCallResponse to send back to the compiler
        """
        from .utils import then_or, catch_or
        
        def execute_function():
            # Get the function (like Node.js get() method)
            function = self._get_function_from_request(request)
            
            # Convert protobuf arguments to Python Values (like Node.js protofier.deprotofy)
            python_args = self._convert_arguments_from_proto(request.arguments)
            
            # Call the function (might return Value or Awaitable[Value])
            result = function(python_args)
            
            # Handle both sync and async results (like Node.js thenOr)
            def process_result(value):
                # Validate result is a Value (like Node.js validation)
                if not isinstance(value, Value):
                    function_name = self._get_function_name_from_request(request)
                    raise CompileException(
                        f'options.functions: "{function_name}" returned non-Value: {type(value).__name__}'
                    )
                
                # Convert result to protobuf (like Node.js protofier.protofy)
                proto_result = self._convert_value_to_proto(value)
                
                # Create success response
                response = proto.InboundMessage.FunctionCallResponse()
                response.success.CopyFrom(proto_result)
                return response
            
            return then_or(result, process_result)
        
        def handle_error(error):
            # Create error response (exactly like Node.js error case)
            response = proto.InboundMessage.FunctionCallResponse()
            response.error = str(error)
            return response
        
        # Use catchOr pattern exactly like Node.js
        return catch_or(execute_function, handle_error)
    
    def _get_function_from_request(self, request: proto.OutboundMessage.FunctionCallRequest) -> SassFunction:
        """
        Get the function referenced by the request (exactly like Node.js get() method).
        
        Args:
            request: The function call request
            
        Returns:
            The function to call
            
        Raises:
            CompileException: If function is not found or request is invalid
        """
        # Handle function by name (matches our protobuf structure)
        if request.name:
            function_name = request.name
            if function_name in self._functions_by_name:
                return self._functions_by_name[function_name]
            raise CompileException(
                f'Invalid OutboundMessage_FunctionCallRequest: there is no function named "{function_name}"'
            )
        
        # Handle function by ID (matches our protobuf structure)
        elif request.function_id:
            function_id = request.function_id
            if function_id in self._functions_by_id:
                return self._functions_by_id[function_id]
            raise CompileException(
                f'Invalid OutboundMessage_FunctionCallRequest: there is no function with ID "{function_id}"'
            )
        
        # If neither field is set, throw error (like Node.js)
        else:
            raise CompileException(
                'Invalid OutboundMessage_FunctionCallRequest: function identifier is unset'
            )
    
    def _get_function_name_from_request(self, request: proto.OutboundMessage.FunctionCallRequest) -> str:
        """Get function name from request for error messages (like Node.js)."""
        if hasattr(request.identifier, 'name') and request.identifier.name:
            return request.identifier.name
        elif hasattr(request, 'name') and request.name:
            return request.name
        else:
            return "anonymous function"
    
    def _convert_arguments_from_proto(self, proto_args: List[Any]) -> List[Value]:
        """
        Convert protobuf arguments to Python Values (like Node.js protofier.deprotofy).
        
        Args:
            proto_args: List of protobuf Value messages
            
        Returns:
            List of Python Sass Values
        """
        from .value_converter import from_proto
        
        converted_args = []
        for arg in proto_args:
            converted_args.append(from_proto(arg))
        return converted_args
    
    def _convert_value_to_proto(self, value: Value) -> Any:
        """
        Convert a Sass value to protobuf format (like Node.js protofier.protofy).
        
        Args:
            value: The Sass value to convert
            
        Returns:
            Protobuf Value message
        """
        from .value_converter import to_proto
        return to_proto(value)
