"""
Request tracker tests based on Node.js reference implementation.
"""

import pytest
from dart_sass.request_tracker import RequestTracker


class TestRequestTrackerReference:
    """Test request tracker following Node.js reference implementation exactly."""
    
    def setup_method(self):
        """Set up a fresh request tracker for each test."""
        self.tracker = RequestTracker()
    
    def test_returns_next_id_when_empty(self):
        """Test that next_id returns 0 when tracker is empty."""
        assert self.tracker.next_id == 0
    
    # Tracking requests tests
    def test_tracks_when_empty(self):
        """Test tracking a single request when tracker is empty."""
        self.tracker.add(0, 'compileResponse')
        assert self.tracker.next_id == 1
    
    def test_tracks_multiple_requests(self):
        """Test tracking multiple requests."""
        self.tracker.add(0, 'compileResponse')
        self.tracker.add(1, 'compileResponse')
        self.tracker.add(2, 'compileResponse')
        assert self.tracker.next_id == 3
    
    def test_tracks_starting_from_non_zero_id(self):
        """Test tracking starting from a non-zero ID."""
        self.tracker.add(1, 'compileResponse')
        assert self.tracker.next_id == 0
        self.tracker.add(0, 'compileResponse')
        assert self.tracker.next_id == 2
    
    def test_errors_if_request_id_is_invalid(self):
        """Test error when request ID is invalid (negative)."""
        with pytest.raises(ValueError, match="Invalid request ID -1"):
            self.tracker.add(-1, 'compileResponse')
    
    def test_errors_if_request_id_overlaps_existing(self):
        """Test error when request ID overlaps existing in-flight request."""
        self.tracker.add(0, 'compileResponse')
        with pytest.raises(ValueError, match="Request ID 0 is already in use by an in-flight request"):
            self.tracker.add(0, 'compileResponse')
    
    # Resolving requests tests
    def test_resolves_single_request(self):
        """Test resolving a single request."""
        self.tracker.add(0, 'compileResponse')
        self.tracker.resolve(0, 'compileResponse')
        assert self.tracker.next_id == 0
    
    def test_resolves_multiple_requests(self):
        """Test resolving multiple requests."""
        self.tracker.add(0, 'compileResponse')
        self.tracker.add(1, 'compileResponse')
        self.tracker.add(2, 'compileResponse')
        self.tracker.resolve(1, 'compileResponse')
        self.tracker.resolve(2, 'compileResponse')
        self.tracker.resolve(0, 'compileResponse')
        assert self.tracker.next_id == 0
    
    def test_reuses_id_of_resolved_request(self):
        """Test that resolved request IDs are reused."""
        self.tracker.add(0, 'compileResponse')
        self.tracker.add(1, 'compileResponse')
        self.tracker.resolve(0, 'compileResponse')
        assert self.tracker.next_id == 0
    
    def test_errors_if_response_id_does_not_match_pending(self):
        """Test error when response ID doesn't match any pending requests."""
        with pytest.raises(ValueError, match="Response ID 0 does not match any pending requests"):
            self.tracker.resolve(0, 'compileResponse')
    
    def test_errors_if_response_type_does_not_match_request(self):
        """Test error when response type doesn't match request type."""
        self.tracker.add(0, 'importResponse')
        with pytest.raises(ValueError, match="Response with ID 0 does not match pending request's type. Expected importResponse but received fileImportResponse"):
            self.tracker.resolve(0, 'fileImportResponse')
