"""
Packet transformer tests based on Node.js reference implementation.
"""

import pytest
from unittest.mock import Mock
import reactivex as rx
from reactivex.subject import Subject
from dart_sass.packet_transformer import PacketTransformer


class TestPacketTransformerReference:
    """Test packet transformer following Node.js reference implementation exactly."""
    
    # Encode tests
    def test_encodes_empty_message(self):
        """Test encoding an empty message."""
        encoded_buffers = []
        packets = PacketTransformer(rx.empty(), lambda buffer: encoded_buffers.append(buffer))
        
        packets.writeInboundProtobuf(b'')
        
        assert encoded_buffers == [b'\x00']
    
    def test_encodes_message_of_length_1(self):
        """Test encoding a message of length 1."""
        encoded_buffers = []
        packets = PacketTransformer(rx.empty(), lambda buffer: encoded_buffers.append(buffer))
        
        packets.writeInboundProtobuf(bytes([123]))
        
        assert encoded_buffers == [bytes([1, 123])]
    
    def test_encodes_message_of_length_greater_than_256(self):
        """Test encoding a message of length greater than 256."""
        encoded_buffers = []
        packets = PacketTransformer(rx.empty(), lambda buffer: encoded_buffers.append(buffer))
        
        message = bytes([1] * 300)
        packets.writeInboundProtobuf(message)
        
        # 300 in varint is [172, 2]
        expected = bytes([172, 2] + [1] * 300)
        assert encoded_buffers == [expected]
    
    def test_encodes_multiple_messages(self):
        """Test encoding multiple messages."""
        encoded_buffers = []
        packets = PacketTransformer(rx.empty(), lambda buffer: encoded_buffers.append(buffer))
        
        packets.writeInboundProtobuf(bytes([10]))
        packets.writeInboundProtobuf(bytes([20, 30]))
        packets.writeInboundProtobuf(bytes([40, 50, 60]))
        
        assert encoded_buffers == [
            bytes([1, 10]),
            bytes([2, 20, 30]),
            bytes([3, 40, 50, 60]),
        ]
    
    # Decode tests
    def test_decodes_empty_message_single_chunk(self):
        """Test decoding an empty message in a single chunk."""
        raw_buffers = Subject()
        packets = PacketTransformer(raw_buffers, lambda x: None)
        
        decoded_messages = []
        packets.outbound_protobufs.subscribe(
            on_next=lambda msg: decoded_messages.append(msg),
            on_completed=lambda: None
        )
        
        raw_buffers.on_next(bytes([0]))
        raw_buffers.on_completed()
        
        assert decoded_messages == [b'']
    
    def test_decodes_empty_message_with_more_data(self):
        """Test decoding an empty message in a chunk that contains more data."""
        raw_buffers = Subject()
        packets = PacketTransformer(raw_buffers, lambda x: None)
        
        decoded_messages = []
        packets.outbound_protobufs.subscribe(
            on_next=lambda msg: decoded_messages.append(msg),
            on_completed=lambda: None
        )
        
        raw_buffers.on_next(bytes([0, 1, 100]))
        raw_buffers.on_completed()
        
        assert decoded_messages == [b'', bytes([100])]
    
    def test_decodes_longer_message_single_chunk(self):
        """Test decoding a longer message in a single chunk."""
        raw_buffers = Subject()
        packets = PacketTransformer(raw_buffers, lambda x: None)
        
        decoded_messages = []
        packets.outbound_protobufs.subscribe(
            on_next=lambda msg: decoded_messages.append(msg),
            on_completed=lambda: None
        )
        
        raw_buffers.on_next(bytes([4, 1, 2, 3, 4]))
        raw_buffers.on_completed()
        
        assert decoded_messages == [bytes([1, 2, 3, 4])]
    
    def test_decodes_longer_message_multiple_chunks(self):
        """Test decoding a longer message across multiple chunks."""
        raw_buffers = Subject()
        packets = PacketTransformer(raw_buffers, lambda x: None)
        
        decoded_messages = []
        packets.outbound_protobufs.subscribe(
            on_next=lambda msg: decoded_messages.append(msg),
            on_completed=lambda: None
        )
        
        # 300 bytes message: varint 300 = [172, 2]
        raw_buffers.on_next(bytes([172]))
        raw_buffers.on_next(bytes([2, 1]))
        raw_buffers.on_next(bytes([1] * 299))
        raw_buffers.on_completed()
        
        assert decoded_messages == [bytes([1] * 300)]
    
    def test_decodes_one_chunk_per_byte(self):
        """Test decoding one chunk per byte."""
        raw_buffers = Subject()
        packets = PacketTransformer(raw_buffers, lambda x: None)
        
        decoded_messages = []
        packets.outbound_protobufs.subscribe(
            on_next=lambda msg: decoded_messages.append(msg),
            on_completed=lambda: None
        )
        
        # Send 300 bytes message one byte at a time
        # Varint 300 = [172, 2], then 300 bytes of 1
        for byte in [172, 2] + [1] * 300:
            raw_buffers.on_next(bytes([byte]))
        raw_buffers.on_completed()
        
        assert decoded_messages == [bytes([1] * 300)]
    
    def test_decodes_chunk_with_more_data(self):
        """Test decoding a chunk that contains more data."""
        raw_buffers = Subject()
        packets = PacketTransformer(raw_buffers, lambda x: None)
        
        decoded_messages = []
        packets.outbound_protobufs.subscribe(
            on_next=lambda msg: decoded_messages.append(msg),
            on_completed=lambda: None
        )
        
        raw_buffers.on_next(bytes([4, 1, 2, 3, 4, 1, 0]))
        raw_buffers.on_completed()
        
        assert decoded_messages == [bytes([1, 2, 3, 4]), bytes([0])]
    
    def test_decodes_full_chunk_length_greater_than_256(self):
        """Test decoding a full chunk of length greater than 256."""
        raw_buffers = Subject()
        packets = PacketTransformer(raw_buffers, lambda x: None)
        
        decoded_messages = []
        packets.outbound_protobufs.subscribe(
            on_next=lambda msg: decoded_messages.append(msg),
            on_completed=lambda: None
        )
        
        # 300 bytes in one chunk: [172, 2] + 300 bytes of 1
        raw_buffers.on_next(bytes([172, 2] + [1] * 300))
        raw_buffers.on_completed()
        
        assert decoded_messages == [bytes([1] * 300)]
    
    def test_decodes_multiple_messages_single_chunk(self):
        """Test decoding multiple messages in a single chunk."""
        raw_buffers = Subject()
        packets = PacketTransformer(raw_buffers, lambda x: None)
        
        decoded_messages = []
        packets.outbound_protobufs.subscribe(
            on_next=lambda msg: decoded_messages.append(msg),
            on_completed=lambda: None
        )
        
        raw_buffers.on_next(bytes([4, 1, 2, 3, 4, 2, 101, 102]))
        raw_buffers.on_completed()
        
        assert decoded_messages == [bytes([1, 2, 3, 4]), bytes([101, 102])]
    
    def test_decodes_multiple_messages_multiple_chunks(self):
        """Test decoding multiple messages across multiple chunks."""
        raw_buffers = Subject()
        packets = PacketTransformer(raw_buffers, lambda x: None)
        
        decoded_messages = []
        packets.outbound_protobufs.subscribe(
            on_next=lambda msg: decoded_messages.append(msg),
            on_completed=lambda: None
        )
        
        raw_buffers.on_next(bytes([4]))
        raw_buffers.on_next(bytes([1, 2, 3, 4, 172]))
        raw_buffers.on_next(bytes([2] + [1] * 300))
        raw_buffers.on_completed()
        
        assert decoded_messages == [bytes([1, 2, 3, 4]), bytes([1] * 300)]
    
    def test_decodes_multiple_messages_one_chunk_per_byte(self):
        """Test decoding multiple messages one chunk per byte."""
        raw_buffers = Subject()
        packets = PacketTransformer(raw_buffers, lambda x: None)
        
        decoded_messages = []
        packets.outbound_protobufs.subscribe(
            on_next=lambda msg: decoded_messages.append(msg),
            on_completed=lambda: None
        )
        
        # First message: 4 bytes [1,2,3,4], then 300 bytes of 1
        for byte in [4, 1, 2, 3, 4, 172, 2] + [1] * 300:
            raw_buffers.on_next(bytes([byte]))
        raw_buffers.on_completed()
        
        assert decoded_messages == [bytes([1, 2, 3, 4]), bytes([1] * 300)]
