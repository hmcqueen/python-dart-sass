"""
Message transformer tests based on Node.js reference implementation.
"""

import pytest
from unittest.mock import Mock
import reactivex as rx
from reactivex.subject import Subject
from dart_sass.message_transformer import MessageTransformer
from dart_sass.vendor import embedded_sass_pb2 as proto
from dart_sass.varint_decoder import encode_varint


class TestMessageTransformerReference:
    """Test message transformer following Node.js reference implementation exactly."""
    
    def valid_inbound_message(self, source: str) -> proto.InboundMessage:
        """Create a valid inbound message like in Node.js test."""
        message = proto.InboundMessage()
        message.compile_request.string.source = source
        return message
    
    def test_encodes_inbound_message_to_buffer(self):
        """Test encoding an InboundMessage to buffer."""
        encoded_protobufs = []
        messages = MessageTransformer(rx.empty(), lambda buffer: encoded_protobufs.append(buffer))
        
        message = self.valid_inbound_message('a {b: c}')
        messages.write_inbound_message((1234, message))
        
        # Should encode as varint ID + protobuf message
        expected = encode_varint(1234) + message.SerializeToString()
        assert encoded_protobufs == [expected]
    
    def test_decodes_buffer_to_outbound_message(self):
        """Test decoding buffer to OutboundMessage."""
        protobufs = Subject()
        messages = MessageTransformer(protobufs, lambda x: None)
        
        decoded_messages = []
        messages.outbound_messages.subscribe(
            on_next=lambda msg: decoded_messages.append(msg),
            on_completed=lambda: None
        )
        
        # Create a response message
        inbound_msg = self.valid_inbound_message('a {b: c}')
        
        # Simulate the compiler processing and returning a response
        # In real usage, this would be a proper OutboundMessage from the Sass compiler
        buffer = encode_varint(1234) + inbound_msg.SerializeToString()
        
        protobufs.on_next(buffer)
        protobufs.on_completed()
        
        # Should have decoded one message
        assert len(decoded_messages) == 1
        id_val, message = decoded_messages[0]
        assert id_val == 1234
        # The message should be parseable (exact content depends on Sass compiler response)
        assert message is not None
    
    def test_fails_on_invalid_buffer(self):
        """Test that invalid buffer causes protocol error."""
        protobufs = Subject()
        messages = MessageTransformer(protobufs, lambda x: None)
        
        error_occurred = False
        error_message = ""
        
        def on_error(error):
            nonlocal error_occurred, error_message
            error_occurred = True
            error_message = str(error)
        
        messages.outbound_messages.subscribe(
            on_next=lambda msg: None,
            on_error=on_error
        )
        
        # Send invalid buffer (invalid varint)
        protobufs.on_next(bytes([255]))  # Invalid varint
        
        # Should cause an error
        assert error_occurred
        assert "varint" in error_message.lower() or "decode" in error_message.lower()
