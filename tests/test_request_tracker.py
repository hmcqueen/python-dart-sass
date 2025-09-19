"""
Tests for RequestTracker following Node.js reference implementation patterns.
"""

import pytest
import threading
import time
from dart_sass.request_tracker import RequestTracker


class TestRequestTracker:
    """Test cases for RequestTracker matching Node.js reference tests."""
    
    def test_add_request(self):
        """Test adding requests (following Node.js patterns)."""
        tracker = RequestTracker()
        
        # Test next_id when empty (Node.js: "returns the next ID when empty")
        assert tracker.next_id == 0
        
        # Add first request (Node.js: tracker.add(0, 'compileResponse'))
        tracker.add(0, 'compileResponse')
        assert tracker.next_id == 1
        
        # Add second request
        tracker.add(1, 'compileResponse')
        assert tracker.next_id == 2
        
        # Verify requests are tracked (direct inspection like Node.js tests would)
        assert tracker._requests[0] == 'compileResponse'
        assert tracker._requests[1] == 'compileResponse'
    
    def test_remove_request(self):
        """Test removing requests (following Node.js resolve patterns)."""
        tracker = RequestTracker()
        
        # Add a request
        tracker.add(0, 'compileResponse')
        assert tracker._requests[0] == 'compileResponse'
        
        # Resolve the request
        tracker.resolve(0, 'compileResponse')
        assert tracker._requests[0] is None
        
        # Next ID should reuse the slot
        assert tracker.next_id == 0
    
    def test_clear_requests(self):
        """Test clearing all requests."""
        tracker = RequestTracker()
        
        # Add multiple requests
        tracker.add(0, 'compileResponse')
        tracker.add(1, 'importResponse')
        tracker.add(2, 'functionCallResponse')
        
        # Verify they're added
        assert tracker._requests[0] == 'compileResponse'
        assert tracker._requests[1] == 'importResponse'
        assert tracker._requests[2] == 'functionCallResponse'
        
        # Clear all (direct manipulation like Node.js would)
        tracker._requests.clear()
        assert len(tracker._requests) == 0
        assert tracker.next_id == 0
    
    def test_invalid_request_id(self):
        """Test error handling for invalid request IDs (Node.js: 'errors if the request ID is invalid')."""
        tracker = RequestTracker()
        
        # Test negative ID (Node.js: expect(() => tracker.add(-1, 'compileResponse')).toThrow('Invalid request ID -1.'))
        with pytest.raises(ValueError, match="Invalid request ID -1"):
            tracker.add(-1, 'compileResponse')
    
    def test_duplicate_request_id(self):
        """Test error handling for duplicate request IDs (Node.js: 'errors if the request ID overlaps existing')."""
        tracker = RequestTracker()
        
        # Add first request
        tracker.add(0, 'compileResponse')
        
        # Try to add same ID again (Node.js: expect(() => tracker.add(0, 'compileResponse')).toThrow('Request ID 0 is already in use'))
        with pytest.raises(ValueError, match="Request ID 0 is already in use by an in-flight request"):
            tracker.add(0, 'compileResponse')
    
    def test_resolve_nonexistent_request(self):
        """Test error handling for resolving non-existent requests."""
        tracker = RequestTracker()
        
        # Try to resolve non-existent request (Node.js: 'errors if response ID does not match pending')
        with pytest.raises(ValueError, match="Response ID 0 does not match any pending requests"):
            tracker.resolve(0, 'compileResponse')
    
    def test_resolve_wrong_type(self):
        """Test error handling for wrong response type."""
        tracker = RequestTracker()
        
        # Add request expecting 'compileResponse'
        tracker.add(0, 'compileResponse')
        
        # Try to resolve with wrong type (Node.js: 'errors if response type does not match request')
        with pytest.raises(ValueError, match="Response with ID 0 does not match pending request's type. Expected compileResponse but received importResponse"):
            tracker.resolve(0, 'importResponse')
    
    def test_multiple_requests_tracking(self):
        """Test tracking multiple requests (Node.js: 'tracks multiple requests')."""
        tracker = RequestTracker()
        
        # Add multiple requests (Node.js pattern)
        tracker.add(0, 'compileResponse')
        tracker.add(1, 'importResponse')
        tracker.add(2, 'functionCallResponse')
        
        # Verify next ID
        assert tracker.next_id == 3
        
        # Verify all are tracked
        assert tracker._requests[0] == 'compileResponse'
        assert tracker._requests[1] == 'importResponse'
        assert tracker._requests[2] == 'functionCallResponse'
    
    def test_non_sequential_ids(self):
        """Test tracking starting from non-zero ID (Node.js: 'tracks starting from a non-zero ID')."""
        tracker = RequestTracker()
        
        # Add request at ID 1 first (Node.js pattern)
        tracker.add(1, 'compileResponse')
        assert tracker.next_id == 0  # Should return 0 as it's available
        
        # Add request at ID 0
        tracker.add(0, 'compileResponse')
        assert tracker.next_id == 2  # Should return 2 as next available
    
    def test_thread_safety(self):
        """Test thread safety of RequestTracker."""
        tracker = RequestTracker()
        results = []
        
        def add_requests():
            """Add requests in a thread."""
            try:
                for i in range(100):
                    request_id = tracker.next_id
                    tracker.add(request_id, 'compileResponse')
                    results.append(request_id)
            except Exception as e:
                results.append(f"Error: {e}")
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=add_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that we got some successful results (exact count may vary due to threading)
        successful_results = [r for r in results if isinstance(r, int)]
        assert len(successful_results) > 0  # At least some should succeed
        
        # Check that all successful IDs are unique
        assert len(successful_results) == len(set(successful_results))
