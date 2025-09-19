"""
Source span deprotofying utilities for Sass embedded host.
"""

from typing import Any, Optional
from .vendor import embedded_sass_pb2 as proto


def deprotofy_source_span(proto_span: Optional[proto.SourceSpan]) -> Any:
    """
    Convert protobuf source span to Sass SourceSpan object.
    
    This matches the Node.js deprotofySourceSpan() function.
    
    Args:
        proto_span: Protobuf source span
        
    Returns:
        Sass SourceSpan object (for now, returns the proto span as-is)
    """
    if not proto_span:
        return None
    
    # For now, return the proto span as-is
    # TODO: Implement proper SourceSpan conversion when we have SourceSpan class
    return proto_span
