"""
Dispatcher for handling compilation requests and responses.
"""

from typing import Dict, Callable, Any, Tuple
import asyncio
import reactivex as rx
from reactivex import operators as ops

from .vendor import embedded_sass_pb2 as proto
from .request_tracker import RequestTracker
from .utils import compiler_error, host_error, then_or


class Dispatcher:
    """
    Dispatches requests, responses, and events for a single compilation.
    
    Accepts callbacks for processing different types of outbound requests. When
    an outbound request arrives, this runs the appropriate callback to process
    it, and then sends the result inbound. A single callback must be provided for
    each outbound request type. The callback does not need to set the response
    ID; the dispatcher handles it.
    
    Consumers can send an inbound request. This returns a promise that will
    either resolve with the corresponding outbound response, or error if any
    Protocol Errors were encountered. The consumer does not need to set the
    request ID; the dispatcher handles it.
    
    Outbound events are exposed as Observables.
    """
    
    def __init__(
        self, 
        compilation_id: int, 
        outbound_messages: rx.Observable[Tuple[int, proto.OutboundMessage]], 
        write_inbound_message: Callable[[Tuple[int, proto.InboundMessage]], None], 
        handlers: Dict[str, Callable]
    ):
        """
        Initialize the dispatcher.
        
        Args:
            compilation_id: The compilation ID for this dispatcher
            outbound_messages: Observable of outbound messages
            write_inbound_message: Function to write inbound messages
            handlers: Dictionary of callback handlers for different message types
        """
        # Validate compilation ID (match Node.js)
        if compilation_id < 1:
            raise Exception(f"Invalid compilation ID {compilation_id}.")
        
        self._compilation_id = compilation_id
        self._outbound_messages = outbound_messages
        self._write_inbound_message = write_inbound_message
        self._handlers = handlers or {}
        
        # Tracks the IDs of all outbound requests (match Node.js pendingOutboundRequests)
        self._pending_outbound_requests = RequestTracker()
        
        # All outbound messages for this compilation (match Node.js messages$)
        self._messages: rx.Subject[proto.OutboundMessage] = rx.Subject()
        
        # Subject to unsubscribe from all messages (match Node.js unsubscribe$)
        self._unsubscribe_subject: rx.Subject[None] = rx.Subject()
        
        # Error handling
        self._error_subject: rx.Subject[Exception] = rx.Subject()
        self.error_observable = self._error_subject.pipe()  # type: ignore[call-overload]
        
        # Outbound log events (match Node.js logEvents$ observable)
        self.log_events = self._messages.pipe(
            ops.filter(lambda msg: msg.HasField('log_event')),  # type: ignore[attr-defined]
            ops.map(lambda msg: msg.log_event)  # type: ignore[attr-defined]
        )
        
        # Set up message processing
        self._setup_message_processing()
    
    def send_compile_request(self, request: proto.InboundMessage.CompileRequest, callback: Callable) -> None:
        """
        Send a compile request and call the callback with the result.
        (Match Node.js sendCompileRequest method exactly)
        
        Args:
            request: The compile request to send
            callback: Function to call with (error, response)
        """
        # Call the callback but unsubscribe first (match Node.js)
        def callback_wrapper(err, response):
            self.unsubscribe()
            return callback(err, response)
        
        # Check if dispatcher is already stopped (match Node.js)
        # Note: RxPY Subject doesn't have isStopped, so we'll track this ourselves
        if hasattr(self._messages, 'is_disposed') and self._messages.is_disposed:
            callback_wrapper(Exception('Tried writing to closed dispatcher'), None)
            return
        
        # Listen for compile response on messages$ (match Node.js - correct message source)
        self._messages.pipe(
            ops.filter(lambda message: message.HasField('compile_response')),  # type: ignore[attr-defined]
            ops.map(lambda message: message.compile_response)  # type: ignore[attr-defined]
        ).subscribe(
            on_next=lambda response: callback_wrapper(None, response)
        )
        
        # Also listen for errors (match Node.js)
        self.error_observable.subscribe(
            on_error=lambda error: callback_wrapper(error, None)
        )
        
        # Send message with proper protobuf structure and try/catch (match Node.js)
        try:
            # Create proper InboundMessage with CompileRequest (Python protobuf way)
            inbound_message = proto.InboundMessage()
            inbound_message.compile_request.CopyFrom(request)
            
            # Match Node.js: this.writeInboundMessage([this.compilationId, message])
            self._write_inbound_message((self._compilation_id, inbound_message))
        except Exception as error:
            self._throw_and_close(error)
    
    def _setup_message_processing(self) -> None:
        """Set up processing for different message types (match Node.js constructor exactly)."""
        # Match Node.js constructor pattern exactly:
        # this.outboundMessages$
        #   .pipe(
        #     filter(([compilationId]) => compilationId === this.compilationId),
        #     map(([, message]) => message),
        #     mergeMap(message => {
        #       const result = this.handleOutboundMessage(message);
        #       return result instanceof Promise
        #         ? result.then(() => message)
        #         : [message];
        #     }),
        #     takeUntil(this.unsubscribe$),
        #   )
        
        def merge_map_handler(message):
            """Handle message and return observable (match Node.js mergeMap exactly)."""
            try:
                # Call handleOutboundMessage (match Node.js)
                result = self._handle_outbound_message(message)
                
                # Match Node.js: return result instanceof Promise ? result.then(() => message) : [message];
                if hasattr(result, '__await__'):
                    # Handle awaitable case - equivalent to result.then(() => message)
                    async def handle_async():
                        await result  # Wait for completion (like .then())
                        return message  # Return original message (like Node.js)
                    
                    return rx.from_future(asyncio.ensure_future(handle_async()))
                else:
                    # Handle synchronous case - equivalent to [message]
                    return rx.of(message)
                    
            except Exception as e:
                return rx.throw(e)
        
        self._outbound_messages.pipe(
            ops.filter(lambda msg: msg[0] == self._compilation_id),  # type: ignore[index]
            ops.map(lambda msg: msg[1]),  # type: ignore[index] # Extract the message
            ops.flat_map(merge_map_handler),  # RxPY uses flat_map instead of merge_map
            ops.take_until(self._unsubscribe_subject)
        ).subscribe(
            on_next=lambda message: self._messages.on_next(message),  # Match Node.js: message => this.messages$.next(message)
            on_error=lambda error: self._throw_and_close(error),      # Match Node.js: error => this.throwAndClose(error)
            on_completed=lambda: self._complete_messages()            # Match Node.js complete handler
        )
    
    def _handle_outbound_message(self, message: proto.OutboundMessage):
        """Handle an outbound message by routing to appropriate handler (match Node.js exactly)."""
        # Get message type - Python equivalent of message.message.case
        message_case = message.WhichOneof('message')
        
        # Use Python 3.10+ match statement - cleaner than Node.js switch!
        match message_case:
            case 'log_event' | 'compile_response':
                # Handled separately by observables
                return None
                
            case 'import_request':
                import_req = message.import_request
                request_id = import_req.id
                response_type = 'importResponse'
                self._pending_outbound_requests.add(request_id, response_type)
                
                def send_response(response):
                    self._send_inbound_message(request_id, {'case': response_type, 'value': response})
                
                return then_or(
                    self._handlers['handleImportRequest'](import_req),
                    send_response
                )
                
            case 'file_import_request':
                file_req = message.file_import_request
                request_id = file_req.id
                response_type = 'fileImportResponse'
                self._pending_outbound_requests.add(request_id, response_type)
                
                def send_response(response):
                    self._send_inbound_message(request_id, {'case': response_type, 'value': response})
                
                return then_or(
                    self._handlers['handleFileImportRequest'](file_req),
                    send_response
                )
                
            case 'canonicalize_request':
                canon_req = message.canonicalize_request
                request_id = canon_req.id
                response_type = 'canonicalizeResponse'
                self._pending_outbound_requests.add(request_id, response_type)
                
                def send_response(response):
                    self._send_inbound_message(request_id, {'case': response_type, 'value': response})
                
                return then_or(
                    self._handlers['handleCanonicalizeRequest'](canon_req),
                    send_response
                )
                
            case 'function_call_request':
                func_req = message.function_call_request
                request_id = func_req.id
                response_type = 'functionCallResponse'
                self._pending_outbound_requests.add(request_id, response_type)
                
                def send_response(response):
                    self._send_inbound_message(request_id, {'case': response_type, 'value': response})
                
                return then_or(
                    self._handlers['handleFunctionCallRequest'](func_req),
                    send_response
                )
                
            case 'error':
                # Match Node.js: throw hostError(message.message.value.message)
                raise host_error(message.error.message)
                
            case _:
                # Match Node.js: throw compilerError(`Unknown message type ${message.message.case}`)
                raise compiler_error(f"Unknown message type {message_case}")
    
    def _send_inbound_message(self, request_id: int, message: Dict[str, Any]) -> None:
        """Send a message inbound with proper request tracking (match Node.js sendInboundMessage exactly)."""
        # Extract case and value from message (match Node.js pattern)
        message_case = message['case']
        response_value = message['value']
        
        # Set the response ID (match Node.js: message.value.id = requestId)
        response_value.id = request_id
        
        # Resolve the pending request (match Node.js)
        if message_case in ['importResponse', 'fileImportResponse', 'canonicalizeResponse', 'functionCallResponse']:
            self._pending_outbound_requests.resolve(request_id, message_case)
        else:
            raise Exception(f"Unknown message type {message_case}")
        
        # Create the inbound message with proper protobuf structure (match Node.js)
        # Node.js: create(proto.InboundMessageSchema, {message})
        inbound_message = proto.InboundMessage()
        
        if message_case == 'functionCallResponse':
            inbound_message.function_call_response.CopyFrom(response_value)
        elif message_case == 'importResponse':
            inbound_message.import_response.CopyFrom(response_value)
        elif message_case == 'fileImportResponse':
            inbound_message.file_import_response.CopyFrom(response_value)
        elif message_case == 'canonicalizeResponse':
            inbound_message.canonicalize_response.CopyFrom(response_value)
        else:
            raise Exception(f"Unknown message case: {message_case}")
        
        # Send the message with compilation ID (match Node.js writeInboundMessage call)
        # Node.js: this.writeInboundMessage([this.compilationId, create(proto.InboundMessageSchema, {message})])
        self._write_inbound_message((self._compilation_id, inbound_message))
    
    def _convert_syntax_to_proto(self, syntax: str) -> int:
        """Convert syntax string to protobuf enum."""
        # Use hardcoded values that match the protobuf enum
        syntax_map = {
            'scss': 0,    # SCSS
            'sass': 1,    # INDENTED
            'css': 2,     # CSS
        }
        
        return syntax_map.get(syntax.lower(), 0)  # Default to SCSS
    
    def _throw_and_close(self, error) -> None:
        """
        Rejects with `error` all promises awaiting an outbound response, and
        silently closes all subscriptions awaiting outbound events.
        (Match Node.js throwAndClose method exactly)
        """
        self._messages.on_completed()
        self._error_subject.on_error(error)
        self.unsubscribe()  # Match Node.js: this.unsubscribe()
    
    def _complete_messages(self) -> None:
        """Complete messages and error subjects (match Node.js complete handler)."""
        self._messages.on_completed()
        self._error_subject.on_completed()
    
    def unsubscribe(self) -> None:
        """Stop the outbound message subscription (match Node.js unsubscribe method exactly)."""
        # Match Node.js: this.unsubscribe$.next(undefined); this.unsubscribe$.complete();
        self._unsubscribe_subject.on_next(None)
        self._unsubscribe_subject.on_completed()
    
    def dispose(self) -> None:
        """Dispose of the dispatcher."""
        self.unsubscribe()
        self._messages.on_completed()
        self._error_subject.on_completed()
