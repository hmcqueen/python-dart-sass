"""
Tests for varint decoder.
"""

import pytest
from dart_sass.varint_decoder import encode_varint, decode_varint


class TestVarintDecoder:
    """Test cases for varint encoding/decoding."""
    
    def test_encode_small_numbers(self):
        """Test encoding small numbers."""
        assert encode_varint(0) == b'\x00'
        assert encode_varint(1) == b'\x01'
        assert encode_varint(127) == b'\x7f'
    
    def test_encode_large_numbers(self):
        """Test encoding numbers that require multiple bytes."""
        assert encode_varint(128) == b'\x80\x01'
        assert encode_varint(300) == b'\xac\x02'
        assert encode_varint(16384) == b'\x80\x80\x01'
    
    def test_decode_small_numbers(self):
        """Test decoding small numbers."""
        value, bytes_consumed = decode_varint(b'\x00')
        assert value == 0
        assert bytes_consumed == 1
        
        value, bytes_consumed = decode_varint(b'\x01')
        assert value == 1
        assert bytes_consumed == 1
        
        value, bytes_consumed = decode_varint(b'\x7f')
        assert value == 127
        assert bytes_consumed == 1
    
    def test_decode_large_numbers(self):
        """Test decoding numbers that require multiple bytes."""
        value, bytes_consumed = decode_varint(b'\x80\x01')
        assert value == 128
        assert bytes_consumed == 2
        
        value, bytes_consumed = decode_varint(b'\xac\x02')
        assert value == 300
        assert bytes_consumed == 2
        
        value, bytes_consumed = decode_varint(b'\x80\x80\x01')
        assert value == 16384
        assert bytes_consumed == 3
    
    def test_decode_with_offset(self):
        """Test decoding with an offset."""
        data = b'\xff\x80\x01\xff'
        value, bytes_consumed = decode_varint(data, offset=1)
        assert value == 128
        assert bytes_consumed == 2
    
    def test_decode_with_extra_data(self):
        """Test decoding when there's extra data after the varint."""
        data = b'\x7f\xff\xff\xff'
        value, bytes_consumed = decode_varint(data)
        assert value == 127
        assert bytes_consumed == 1
    
    def test_roundtrip(self):
        """Test encoding and then decoding gives the same result."""
        test_values = [0, 1, 127, 128, 300, 16384, 2097151, 268435455]
        
        for original_value in test_values:
            encoded = encode_varint(original_value)
            decoded_value, bytes_consumed = decode_varint(encoded)
            
            assert decoded_value == original_value
            assert bytes_consumed == len(encoded)
    
    def test_incomplete_varint(self):
        """Test handling of incomplete varints."""
        # A varint that starts but doesn't finish
        with pytest.raises(ValueError, match="Incomplete varint"):
            decode_varint(b'\x80')  # Continuation bit set but no more bytes
    
    def test_empty_data(self):
        """Test handling of empty data."""
        with pytest.raises(ValueError, match="Not enough data"):
            decode_varint(b'')
    
    def test_varint_too_long(self):
        """Test handling of varints that are too long."""
        # Create a varint with too many bytes (all with continuation bit set)
        long_varint = b'\x80' * 10 + b'\x01'
        with pytest.raises(ValueError, match="Varint too long"):
            decode_varint(long_varint)
    
    def test_negative_encoding(self):
        """Test that negative numbers raise an error."""
        with pytest.raises(ValueError, match="Cannot encode negative numbers"):
            encode_varint(-1)
