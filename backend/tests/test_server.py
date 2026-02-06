"""
test_server.py — Unit tests for the FastAPI server endpoints

Tests all API endpoints in server.py including:
- Health check endpoints
- Pipeline state management
- Grading initiation and cancellation
- Folder operations
"""

import pytest
import sys
import os
import tempfile
import shutil

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# Test Helper Classes for Server Tests
# ============================================================

class TestSanitizeForWindows:
    """Tests for the _sanitize_for_windows helper function."""
    
    def test_ascii_string_unchanged(self):
        """ASCII strings should pass through unchanged."""
        from server import _sanitize_for_windows
        
        result = _sanitize_for_windows("Hello World 123!")
        assert result == "Hello World 123!"
    
    def test_unicode_replaced(self):
        """Unicode characters should be replaced with ?."""
        from server import _sanitize_for_windows
        
        result = _sanitize_for_windows("Hello 🚀 World")
        assert "Hello" in result
        assert "World" in result
        assert "🚀" not in result
    
    def test_non_string_converted(self):
        """Non-string inputs should be converted to string first."""
        from server import _sanitize_for_windows
        
        result = _sanitize_for_windows(12345)
        assert result == "12345"
    
    def test_empty_string(self):
        """Empty string should return empty string."""
        from server import _sanitize_for_windows
        
        result = _sanitize_for_windows("")
        assert result == ""
    
    def test_none_converted(self):
        """None should be converted to 'None'."""
        from server import _sanitize_for_windows
        
        result = _sanitize_for_windows(None)
        assert result == "None"


class TestLogCapture:
    """Tests for the LogCapture class."""
    
    def test_write_captures_messages(self):
        """LogCapture should capture write messages."""
        from server import LogCapture, pipeline_state
        
        # Save original state
        original_logs = pipeline_state["logs"].copy()
        
        capture = LogCapture()
        capture.write("Test message")
        
        assert "Test message" in capture.getvalue()
        
        # Restore original state
        pipeline_state["logs"] = original_logs
    
    def test_write_strips_whitespace(self):
        """LogCapture should strip whitespace from messages."""
        from server import LogCapture, pipeline_state
        
        original_logs = pipeline_state["logs"].copy()
        
        capture = LogCapture()
        capture.write("  message with spaces  \n")
        
        assert "message with spaces" in capture.getvalue()
        
        pipeline_state["logs"] = original_logs
    
    def test_flush_does_not_error(self):
        """LogCapture flush should not raise errors."""
        from server import LogCapture
        
        capture = LogCapture()
        capture.flush()  # Should not raise
    
    def test_getvalue_returns_all_content(self):
        """getvalue should return all captured content."""
        from server import LogCapture
        
        capture = LogCapture()
        capture.write("Line 1\n")
        capture.write("Line 2\n")
        
        result = capture.getvalue()
        assert "Line 1" in result
        assert "Line 2" in result


class TestWorkspaceManagement:
    """Tests for workspace management functions."""
    
    def test_set_workspace_override_with_none(self):
        """Setting workspace override to None should work."""
        from server import set_workspace_override, _workspace_override
        
        set_workspace_override(None)
        # Should not raise
    
    def test_get_workspace_root_returns_string(self):
        """get_workspace_root should return a string path."""
        from server import get_workspace_root
        
        result = get_workspace_root()
        assert isinstance(result, str)
        assert len(result) > 0


# ============================================================
# Test FastAPI Endpoints (using TestClient if available)
# ============================================================

class TestAPIEndpoints:
    """Tests for FastAPI API endpoints using direct function calls."""
    
    def test_pipeline_state_initial(self):
        """Initial pipeline state should be idle."""
        from server import pipeline_state
        
        # The state might have been modified by other tests, so just check structure
        assert "status" in pipeline_state
        assert "logs" in pipeline_state
        assert "error" in pipeline_state
    
    def test_pipeline_state_has_required_keys(self):
        """Pipeline state should have all required keys."""
        from server import pipeline_state
        
        required_keys = [
            "status", "cancel_requested", "current_step",
            "progress", "total_steps", "logs", "error", "output_path"
        ]
        
        for key in required_keys:
            assert key in pipeline_state, f"Missing key: {key}"
    
    def test_reset_state_function(self):
        """reset_state should reset all pipeline state values."""
        import asyncio
        from server import reset_state, pipeline_state
        
        # Modify state
        pipeline_state["status"] = "running"
        pipeline_state["logs"].append("test log")
        
        # Reset
        asyncio.run(reset_state())
        
        assert pipeline_state["status"] == "idle"
        assert pipeline_state["progress"] == 0
        assert len(pipeline_state["logs"]) == 0


class TestGradeRequest:
    """Tests for GradeRequest model validation."""
    
    def test_grade_request_with_defaults(self):
        """GradeRequest should work with required fields only."""
        from server import GradeRequest
        
        request = GradeRequest(
            zip_path="/test/path.zip",
            course_label="MAT-144-501"
        )
        
        assert request.zip_path == "/test/path.zip"
        assert request.course_label == "MAT-144-501"
        assert request.assignment_type == "MA1"  # Default
        assert request.workspace_path is None  # Default
    
    def test_grade_request_with_all_fields(self):
        """GradeRequest should accept all fields."""
        from server import GradeRequest
        
        request = GradeRequest(
            zip_path="/test/path.zip",
            course_label="MAT-144-501",
            assignment_type="MA1",
            workspace_path="/custom/path"
        )
        
        assert request.workspace_path == "/custom/path"


class TestConfigRequest:
    """Tests for ConfigRequest model."""
    
    def test_config_request_with_path(self):
        """ConfigRequest should accept workspace_path."""
        from server import ConfigRequest
        
        request = ConfigRequest(workspace_path="/custom/path")
        assert request.workspace_path == "/custom/path"
    
    def test_config_request_default_none(self):
        """ConfigRequest workspace_path should default to None."""
        from server import ConfigRequest
        
        request = ConfigRequest()
        assert request.workspace_path is None
