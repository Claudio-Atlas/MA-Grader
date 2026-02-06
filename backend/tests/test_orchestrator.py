"""
test_orchestrator.py — Unit tests for orchestrator modules

Tests orchestrator/ modules including:
- grade_single: Single file grading
- phase1_grade_all: Batch grading
- phase2_export_charts: Chart export (Windows only)
- phase3_insert_charts: Chart insertion
- phase4_cleanup: Temp file cleanup
"""

import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch, mock_open

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# Test phase4_cleanup
# ============================================================

class TestPhase4Cleanup:
    """Tests for phase4_cleanup module."""
    
    def test_cleanup_removes_entire_folder(self):
        """Cleanup should remove the entire temp directory."""
        from orchestrator.phase4_cleanup import phase4_cleanup_temp
        
        # Create temp directory with test files
        temp_dir = tempfile.mkdtemp(prefix="test_cleanup_")
        
        # Create some PNG files
        test_files = ["chart1.png", "chart2.png", "chart3.png"]
        for f in test_files:
            open(os.path.join(temp_dir, f), 'w').close()
        
        # Run cleanup
        phase4_cleanup_temp(temp_dir)
        
        # Verify entire folder is removed
        assert not os.path.exists(temp_dir), "Folder should be deleted"
    
    def test_cleanup_nonexistent_directory(self):
        """Cleanup should handle non-existent directory gracefully."""
        from orchestrator.phase4_cleanup import phase4_cleanup_temp
        
        # Should not raise an error
        phase4_cleanup_temp("/path/that/does/not/exist/123456")
    
    def test_cleanup_empty_directory(self):
        """Cleanup should delete empty directory too."""
        from orchestrator.phase4_cleanup import phase4_cleanup_temp
        
        temp_dir = tempfile.mkdtemp(prefix="test_cleanup_empty_")
        
        # Run cleanup
        phase4_cleanup_temp(temp_dir)
        
        # Empty folder should also be deleted
        assert not os.path.exists(temp_dir), "Empty folder should be deleted"


# ============================================================
# Test grade_single
# ============================================================

class TestGradeSingle:
    """Tests for grade_single module."""
    
    @patch('orchestrator.grade_single.load_workbook')
    @patch('orchestrator.grade_single.validate_required_sheets')
    def test_grade_single_file_missing_submission(self, mock_validate, mock_load):
        """Should raise error for missing submission file."""
        from orchestrator.grade_single import grade_single_file
        
        with pytest.raises(FileNotFoundError):
            grade_single_file(
                "/nonexistent/path.xlsx",
                "/some/output/folder"
            )
    
    @patch('orchestrator.grade_single.load_workbook')
    def test_grade_single_file_missing_output_folder(self, mock_load):
        """Should raise error for missing output folder."""
        from orchestrator.grade_single import grade_single_file
        
        # Create a temp file to simulate submission
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        temp_file.close()
        
        try:
            with pytest.raises(FileNotFoundError):
                grade_single_file(
                    temp_file.name,
                    "/nonexistent/output/folder"
                )
        finally:
            os.unlink(temp_file.name)


# ============================================================
# Test phase2_export_charts
# ============================================================

class TestPhase2ExportCharts:
    """Tests for phase2_export_charts module."""
    
    def test_export_charts_nonexistent_path(self):
        """Should raise error for non-existent submission path."""
        from orchestrator.phase2_export_charts import phase2_export_all_charts
        
        # This will raise FileNotFoundError because the path doesn't exist
        with pytest.raises(FileNotFoundError):
            phase2_export_all_charts("/nonexistent/path/to/submissions")
    
    @patch('sys.platform', 'darwin')
    def test_chart_export_skipped_on_mac(self):
        """Chart export should be skipped on macOS."""
        from orchestrator.phase2_export_charts import phase2_export_all_charts
        
        temp_dir = tempfile.mkdtemp()
        try:
            # Should complete without error on Mac (chart export is Windows-only)
            phase2_export_all_charts(temp_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================
# Test phase3_insert_charts
# ============================================================

class TestPhase3InsertCharts:
    """Tests for phase3_insert_charts module."""
    
    def test_insert_charts_nonexistent_path(self):
        """Should handle non-existent graded path gracefully."""
        from orchestrator.phase3_insert_charts import phase3_insert_all_charts
        
        # Should not raise an error
        phase3_insert_all_charts("/nonexistent/path/to/graded")
    
    def test_insert_charts_empty_directory(self):
        """Should handle empty graded directory."""
        from orchestrator.phase3_insert_charts import phase3_insert_all_charts
        
        temp_dir = tempfile.mkdtemp()
        try:
            phase3_insert_all_charts(temp_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================
# Test phase1_grade_all
# ============================================================

class TestPhase1GradeAll:
    """Tests for phase1_grade_all module."""
    
    def test_grade_all_nonexistent_paths(self):
        """Should handle non-existent paths gracefully."""
        from orchestrator.phase1_grade_all import phase1_grade_all_students
        
        # Create empty temp directories
        submissions_dir = tempfile.mkdtemp()
        graded_dir = tempfile.mkdtemp()
        
        try:
            # Should complete without error
            phase1_grade_all_students(submissions_dir, graded_dir)
        finally:
            shutil.rmtree(submissions_dir, ignore_errors=True)
            shutil.rmtree(graded_dir, ignore_errors=True)
    
    def test_grade_all_with_cancellation(self):
        """Should stop on cancellation request."""
        from orchestrator.phase1_grade_all import phase1_grade_all_students
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Set up cancellation state
            pipeline_state = {
                "cancel_requested": True,
                "status": "running"
            }
            
            phase1_grade_all_students(temp_dir, temp_dir, pipeline_state)
            # Should complete early due to cancellation
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_grade_all_empty_submissions(self):
        """Should handle empty submissions folder."""
        from orchestrator.phase1_grade_all import phase1_grade_all_students
        
        submissions_dir = tempfile.mkdtemp()
        graded_dir = tempfile.mkdtemp()
        
        try:
            # Should log that no files were found
            phase1_grade_all_students(submissions_dir, graded_dir)
        finally:
            shutil.rmtree(submissions_dir, ignore_errors=True)
            shutil.rmtree(graded_dir, ignore_errors=True)


# ============================================================
# Test Orchestrator Module Imports
# ============================================================

class TestOrchestratorImports:
    """Test that all orchestrator modules can be imported."""
    
    def test_import_grade_single(self):
        """Should import grade_single module."""
        from orchestrator.grade_single import grade_single_file
        assert callable(grade_single_file)
    
    def test_import_phase1(self):
        """Should import phase1_grade_all module."""
        from orchestrator.phase1_grade_all import phase1_grade_all_students
        assert callable(phase1_grade_all_students)
    
    def test_import_phase2(self):
        """Should import phase2_export_charts module."""
        from orchestrator.phase2_export_charts import phase2_export_all_charts
        assert callable(phase2_export_all_charts)
    
    def test_import_phase3(self):
        """Should import phase3_insert_charts module."""
        from orchestrator.phase3_insert_charts import phase3_insert_all_charts
        assert callable(phase3_insert_all_charts)
    
    def test_import_phase4(self):
        """Should import phase4_cleanup module."""
        from orchestrator.phase4_cleanup import phase4_cleanup_temp
        assert callable(phase4_cleanup_temp)
    
    def test_import_from_init(self):
        """Should import all phases from __init__."""
        from orchestrator import (
            phase1_grade_all_students,
            phase2_export_all_charts,
            phase3_insert_all_charts,
            phase4_cleanup_temp
        )
        
        assert callable(phase1_grade_all_students)
        assert callable(phase2_export_all_charts)
        assert callable(phase3_insert_all_charts)
        assert callable(phase4_cleanup_temp)
