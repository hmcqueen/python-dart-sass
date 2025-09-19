"""
Request tracker for managing request IDs following Node.js reference implementation.
"""

import threading
from typing import List, Optional


class RequestTracker:
    """
    Manages pending inbound and outbound requests. Ensures that requests and
    responses interact correctly and obey the Embedded Protocol.
    
    This follows the Node.js reference implementation exactly.
    """
    
    def __init__(self):
        """Initialize the request tracker."""
        # The indices of this array correspond to each pending request's ID.
        # Stores the response type expected by each request.
        self._requests: List[Optional[str]] = []
        self._lock = threading.Lock()
    
    @property
    def next_id(self) -> int:
        """The next available request ID."""
        with self._lock:
            for i in range(len(self._requests)):
                if self._requests[i] is None:
                    return i
            return len(self._requests)
    
    def add(self, id: int, expected_response_type: str) -> None:
        """
        Adds an entry for a pending request with ID `id`. The entry stores the
        expected response type. Throws an error if the Protocol Error is violated.
        
        Args:
            id: The request ID
            expected_response_type: The expected response type (e.g., 'compileResponse')
        """
        with self._lock:
            if id < 0:
                raise ValueError(f"Invalid request ID {id}.")
            
            # Extend the list if necessary
            while len(self._requests) <= id:
                self._requests.append(None)
            
            if self._requests[id] is not None:
                raise ValueError(f"Request ID {id} is already in use by an in-flight request.")
            
            self._requests[id] = expected_response_type
    
    def resolve(self, id: int, response_type: str) -> None:
        """
        Resolves a pending request with matching ID `id` and expected response type
        `type`. Throws an error if the Protocol Error is violated.
        
        Args:
            id: The request ID
            response_type: The actual response type received
        """
        with self._lock:
            if id >= len(self._requests) or self._requests[id] is None:
                raise ValueError(f"Response ID {id} does not match any pending requests.")
            
            expected_type = self._requests[id]
            if expected_type != response_type:
                raise ValueError(
                    f"Response with ID {id} does not match pending request's type. "
                    f"Expected {expected_type} but received {response_type}."
                )
            
            self._requests[id] = None
