"""
Custom varint decoder that returns both value and bytes consumed.
"""

from typing import Tuple, Optional


def decode_varint(data: bytes, offset: int = 0) -> Tuple[int, int]:
    """
    Decode a varint from bytes and return both the value and bytes consumed.
    
    Args:
        data: The bytes to decode from
        offset: The offset to start decoding from
        
    Returns:
        A tuple of (decoded_value, bytes_consumed)
        
    Raises:
        ValueError: If the varint is invalid or incomplete
    """
    if not data or offset >= len(data):
        raise ValueError("Not enough data to decode varint")
    
    result = 0
    shift = 0
    bytes_consumed = 0
    
    for i in range(offset, len(data)):
        byte = data[i]
        bytes_consumed += 1
        
        # Extract the 7 data bits
        result |= (byte & 0x7F) << shift
        
        # If the continuation bit is not set, we're done
        if (byte & 0x80) == 0:
            return result, bytes_consumed
        
        shift += 7
        
        # Prevent infinite loops with malformed data
        if shift >= 64:
            raise ValueError("Varint too long")
    
    # If we get here, the varint was incomplete
    raise ValueError("Incomplete varint")


def encode_varint(value: int) -> bytes:
    """
    Encode an integer as a varint.
    
    Args:
        value: The integer to encode
        
    Returns:
        The encoded varint bytes
    """
    if value < 0:
        raise ValueError("Cannot encode negative numbers")
    
    result = bytearray()
    
    while value >= 0x80:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    
    result.append(value & 0x7F)
    
    return bytes(result)
