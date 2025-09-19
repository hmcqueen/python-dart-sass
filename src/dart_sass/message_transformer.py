"""
Message transformer for encoding/decoding protocol buffer messages.
"""

from typing import Tuple, Callable
import reactivex as rx
from reactivex import operators as ops

from .vendor import embedded_sass_pb2 as proto
from .utils import compiler_error
from .varint_decoder import decode_varint, encode_varint


class MessageTransformer:
    """
    Encodes InboundMessages into protocol buffers and decodes protocol buffers
    into OutboundMessages.
    """
    
    def __init__(self, outbound_protobufs: rx.Observable, write_inbound_protobuf: Callable[[bytes], None]):
        """
        Initialize the message transformer.
        
        Args:
            outbound_protobufs: Observable of outbound protobuf bytes
            write_inbound_protobuf: Callback to write inbound protobuf bytes
        """
        self.outbound_protobufs = outbound_protobufs
        self.write_inbound_protobuf = write_inbound_protobuf
        
        # The decoded messages are written to this Subject. It is publicly exposed
        # as a readonly Observable.
        self._outbound_messages_internal = rx.Subject()
        
        # The OutboundMessages, decoded from protocol buffers. If this fails to
        # decode a message, it will emit an error.
        self.outbound_messages = self._outbound_messages_internal.pipe()
        
        # Set up the decoding pipeline (exactly like Node.js)
        self.outbound_protobufs.pipe(
            ops.map(self._decode)
        ).subscribe(self._outbound_messages_internal)
    
    def write_inbound_message(self, compilation_id_and_message: tuple) -> None:
        """
        Converts the inbound compilation_id and message to a protocol buffer.
        
        Args:
            compilation_id_and_message: [compilation_id, message] tuple like Node.js
        """
        compilation_id, message = compilation_id_and_message
        
        try:
            # Encode compilation ID as varint (like Node.js)
            compilation_id_bytes = encode_varint(compilation_id)
            
            # Serialize the protobuf message (like Node.js toBinary)
            encoded_message = message.SerializeToString()
            
            # Combine compilation ID and message (like Node.js)
            buffer = compilation_id_bytes + encoded_message
            
            # Write through the callback (like Node.js)
            self.write_inbound_protobuf(buffer)
            
        except Exception as error:
            # Emit error to outbound messages (like Node.js)
            self._outbound_messages_internal.on_error(error)
    
    def _decode(self, buffer: bytes) -> Tuple[int, proto.OutboundMessage]:
        """
        Decodes a protobuf buffer into a compilation ID and an OutboundMessage.
        
        This matches the Node.js decode function exactly.
        
        Args:
            buffer: The protobuf buffer to decode
            
        Returns:
            Tuple of (compilation_id, outbound_message)
        """
        try:
            # Decode compilation ID varint (like Node.js varint.decode)
            compilation_id, varint_bytes = decode_varint(buffer)
        except Exception as error:
            raise compiler_error(f"Invalid compilation ID varint: {error}")
        
        try:
            # Parse the remaining bytes as protobuf (like Node.js fromBinary)
            message = proto.OutboundMessage()
            message.ParseFromString(buffer[varint_bytes:])
            return compilation_id, message
        except Exception as error:
            raise compiler_error(f"Invalid protobuf: {error}")
