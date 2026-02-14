"""
test_orchestrator.py — Unit tests for orchestrator modules

Tests orchestrator/ modules including:
- grade_single: Single file grading
- phase1_grade_all: Batch grading (MA1)
- phase1_grade_all_ma3: Batch grading (MA3)

Note: phase2_export_charts, phase3_insert_charts, and phase4_cleanup were
removed in the 2026-02-08 pipeline simplification (8 steps → 6 steps).
All grading is now done via openpyxl without chart export/import phases.
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
# Test phase1_grade_all_ma3
# ============================================================

class TestPhase1GradeAllMA3:
    """Tests for phase1_grade_all_ma3 module."""
    
    def test_ma3_grade_all_nonexistent_paths(self):
        """Should handle non-existent paths gracefully."""
        from orchestrator.phase1_grade_all_ma3 import phase1_grade_all_students_ma3
        
        # Create empty temp directories
        submissions_dir = tempfile.mkdtemp()
        graded_dir = tempfile.mkdtemp()
        
        try:
            # Should complete without error
            phase1_grade_all_students_ma3(submissions_dir, graded_dir)
        finally:
            shutil.rmtree(submissions_dir, ignore_errors=True)
            shutil.rmtree(graded_dir, ignore_errors=True)
    
    def test_ma3_grade_all_empty_submissions(self):
        """Should handle empty submissions folder."""
        from orchestrator.phase1_grade_all_ma3 import phase1_grade_all_students_ma3
        
        submissions_dir = tempfile.mkdtemp()
        graded_dir = tempfile.mkdtemp()
        
        try:
            # Should log that no files were found
            phase1_grade_all_students_ma3(submissions_dir, graded_dir)
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
    
    def test_import_phase1_ma3(self):
        """Should import phase1_grade_all_ma3 module."""
        from orchestrator.phase1_grade_all_ma3 import phase1_grade_all_students_ma3
        assert callable(phase1_grade_all_students_ma3)
    
    def test_import_from_init(self):
        """Should import all phases from __init__."""
        from orchestrator import (
            phase1_grade_all_students,
            phase1_grade_all_students_ma3,
        )
        
        assert callable(phase1_grade_all_students)
        assert callable(phase1_grade_all_students_ma3)
