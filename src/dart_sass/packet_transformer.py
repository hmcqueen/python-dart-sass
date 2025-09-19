"""
Packet transformer for handling varint length-prefixed packets.
"""

from typing import List, Callable, Optional
import reactivex as rx
from reactivex import operators as ops

from .varint_decoder import encode_varint, decode_varint


class Packet:
    """A length-delimited packet comprised of a header and payload."""
    
    def __init__(self):
        """Initialize a new packet."""
        self.payload_length_bits = 0
        self.payload_length = 0
        self.payload: Optional[bytearray] = None
        self.payload_offset = 0
    
    @property
    def is_complete(self) -> bool:
        """Whether the packet construction is complete."""
        return self.payload is not None and self.payload_offset >= self.payload_length
    
    def write(self, source: bytes) -> int:
        """
        Takes arbitrary binary input and slots it into the header and payload
        appropriately. Returns the number of bytes that were written into the
        packet. This method can be called repeatedly, incrementally building
        up the packet until it is complete.
        
        Args:
            source: The source bytes to write
            
        Returns:
            Number of bytes consumed from source
        """
        if self.is_complete:
            raise ValueError("Cannot write to a completed Packet")
        
        # The index of the next byte to read from source
        i = 0
        
        # If payload is None, we're reading the varint length
        if self.payload is None:
            while i < len(source):
                byte = source[i]
                
                # Varints encode data in the 7 lower bits of each byte
                self.payload_length += (byte & 0x7f) << self.payload_length_bits
                self.payload_length_bits += 7
                i += 1
                
                if byte <= 0x7f:
                    # High bit is unset, we now know the full message length
                    self.payload = bytearray(self.payload_length)
                    break
                # Otherwise continue reading bytes to fill in payload_length
            
            # If we've consumed all source bytes while reading length, return
            if i >= len(source):
                return i
        
        # Copy as many bytes as we can from source to payload
        if self.payload is not None:
            bytes_to_write = min(
                len(self.payload) - self.payload_offset,
                len(source) - i
            )
            
            if bytes_to_write > 0:
                self.payload[self.payload_offset:self.payload_offset + bytes_to_write] = source[i:i + bytes_to_write]
                self.payload_offset += bytes_to_write
            
            return i + bytes_to_write
        
        return i


class PacketTransformer:
    """
    Decodes arbitrarily-chunked buffers into packets of set length and
    encodes packets by attaching a header that describes the payload's length.
    """
    
    def __init__(self, outbound_buffers: rx.Observable, write_inbound_buffer: Callable[[bytes], None]):
        """
        Initialize the packet transformer.
        
        Args:
            outbound_buffers: Observable of outbound buffer chunks
            write_inbound_buffer: Callback to write inbound buffers
        """
        self.outbound_buffers = outbound_buffers
        self.write_inbound_buffer = write_inbound_buffer
        
        # The packet that is actively being decoded
        self.packet = Packet()
        
        # The decoded protobufs are written to this Subject
        self._outbound_protobufs_internal = rx.Subject()
        
        # Public observable for outbound protobufs (match Node.js naming)
        self.outbound_protobufs = self._outbound_protobufs_internal.pipe()
        
        # Set up the decoding pipeline (try concat_map approach)
        def decode_and_emit(buffer):
            payloads = self._decode(buffer)
            for payload in payloads:
                self._outbound_protobufs_internal.on_next(payload)
        
        self.outbound_buffers.subscribe(
            on_next=decode_and_emit,
            on_error=lambda e: self._outbound_protobufs_internal.on_error(e),
            on_completed=lambda: self._outbound_protobufs_internal.on_completed()
        )
    
    def writeInboundProtobuf(self, protobuf: bytes) -> None:
        """
        Encodes a packet by pre-fixing protobuf with a header that describes its length.
        
        Args:
            protobuf: The protobuf bytes to encode
        """
        try:
            length = len(protobuf)
            
            if length == 0:
                self.write_inbound_buffer(bytes([0]))
                return
            
            # Encode the length as varint
            length_bytes = encode_varint(length)
            
            # Combine length header and protobuf payload
            packet = length_bytes + protobuf
            self.write_inbound_buffer(packet)
            
        except Exception as error:
            self._outbound_protobufs_internal.on_error(error)
    
    # Compatibility alias for existing code
    def write_inbound_protobuf(self, protobuf: bytes) -> None:
        """Compatibility alias for writeInboundProtobuf."""
        return self.writeInboundProtobuf(protobuf)
    
    def _decode(self, buffer: bytes) -> List[bytes]:
        """
        Decodes a buffer, filling up the packet that is actively being decoded.
        Returns a list of decoded payloads.
        
        Args:
            buffer: The buffer to decode
            
        Returns:
            List of decoded protobuf payloads
        """
        payloads = []
        decoded_bytes = 0
        
        while decoded_bytes < len(buffer):
            bytes_consumed = self.packet.write(buffer[decoded_bytes:])
            decoded_bytes += bytes_consumed
            
            if self.packet.is_complete and self.packet.payload is not None:
                payloads.append(bytes(self.packet.payload))
                self.packet = Packet()
        
        return payloads
    
    def dispose(self) -> None:
        """Dispose of the packet transformer."""
        self._outbound_protobufs_internal.on_completed()
