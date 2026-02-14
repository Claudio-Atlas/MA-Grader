"""
test_zip_security.py — Tests for ZIP extraction security

Tests that the ZIP extraction code properly prevents path traversal attacks
(ZIP slip vulnerability).
"""

import pytest
import os
import sys
import tempfile
import zipfile

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from writers.import_zip_to_student_groups import _is_safe_path, _safe_extract


class TestPathSafety:
    """Tests for _is_safe_path function."""
    
    def test_safe_path_in_directory(self):
        """Normal path inside directory should be safe."""
        assert _is_safe_path("/tmp/extract", "/tmp/extract/file.xlsx") is True
    
    def test_safe_path_nested(self):
        """Nested path inside directory should be safe."""
        assert _is_safe_path("/tmp/extract", "/tmp/extract/student/file.xlsx") is True
    
    def test_unsafe_path_traversal(self):
        """Path with .. traversal should be blocked."""
        # This simulates what a malicious ZIP would try
        assert _is_safe_path("/tmp/extract", "/tmp/etc/passwd") is False
    
    def test_unsafe_path_absolute(self):
        """Absolute path outside directory should be blocked."""
        assert _is_safe_path("/tmp/extract", "/etc/passwd") is False
    
    def test_safe_path_same_directory(self):
        """Path that equals the base should be safe."""
        assert _is_safe_path("/tmp/extract", "/tmp/extract") is True


class TestSafeExtract:
    """Tests for _safe_extract function."""
    
    def test_safe_zip_extracts(self):
        """Normal ZIP should extract successfully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a safe ZIP
            zip_path = os.path.join(tmpdir, "safe.zip")
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("student/file.xlsx", b"test content")
            
            # Extract it
            extract_dir = os.path.join(tmpdir, "extract")
            os.makedirs(extract_dir)
            
            with zipfile.ZipFile(zip_path, "r") as zf:
                _safe_extract(zf, extract_dir)
            
            # Verify file was extracted
            assert os.path.exists(os.path.join(extract_dir, "student", "file.xlsx"))
    
    def test_malicious_zip_blocked(self):
        """ZIP with path traversal should be blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a malicious ZIP with path traversal
            zip_path = os.path.join(tmpdir, "evil.zip")
            with zipfile.ZipFile(zip_path, "w") as zf:
                # This is what a ZIP slip attack looks like
                zf.writestr("../../../etc/passwd", b"malicious content")
            
            extract_dir = os.path.join(tmpdir, "extract")
            os.makedirs(extract_dir)
            
            with zipfile.ZipFile(zip_path, "r") as zf:
                with pytest.raises(ValueError, match="path traversal"):
                    _safe_extract(zf, extract_dir)
