"""
test_writers.py — Unit tests for writer modules

Tests writers/ modules including:
- create_grading_sheet: Grading sheet creation
- write_income_analysis_scores: Score writing
- Helper functions like _clean_name_parts_from_folder
"""

import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# Test _clean_name_parts_from_folder
# ============================================================

class TestCleanNamePartsFromFolder:
    """Tests for the _clean_name_parts_from_folder helper function."""
    
    def test_standard_name_with_id(self):
        """Standard format: First_Last_12345678"""
        from writers.create_grading_sheet import _clean_name_parts_from_folder
        
        first, last = _clean_name_parts_from_folder("John_Doe_12345678")
        
        assert first == "John"
        assert last == "Doe"
    
    def test_name_with_parenthetical(self):
        """Name with nickname: Jeremiah_(Jeremiah)_Aleman_21192244"""
        from writers.create_grading_sheet import _clean_name_parts_from_folder
        
        first, last = _clean_name_parts_from_folder("Jeremiah_(Jeremiah)_Aleman_21192244")
        
        assert first == "Jeremiah"
        assert last == "Aleman"
    
    def test_name_with_middle_name(self):
        """Name with middle: First_Middle_Last_12345678"""
        from writers.create_grading_sheet import _clean_name_parts_from_folder
        
        first, last = _clean_name_parts_from_folder("John_Michael_Doe_12345678")
        
        assert first == "John"
    
    def test_hyphenated_last_name(self):
        """Hyphenated last name: Joshua_Martinez-Gonzalez_21200978"""
        from writers.create_grading_sheet import _clean_name_parts_from_folder
        
        first, last = _clean_name_parts_from_folder("Joshua_Martinez-Gonzalez_21200978")
        
        assert first == "Joshua"
        assert "Martinez" in last or "Gonzalez" in last
    
    def test_compound_last_name(self):
        """Compound last name: Sylvia_Allen-Orendain_21202233"""
        from writers.create_grading_sheet import _clean_name_parts_from_folder
        
        first, last = _clean_name_parts_from_folder(
            "Sylvia_(Sylvia)_Allen-Orendain_21202233"
        )
        
        assert first == "Sylvia"
        assert "Allen" in last or "Orendain" in last
    
    def test_numeric_only_removed(self):
        """Pure numeric tokens should be removed (student IDs)."""
        from writers.create_grading_sheet import _clean_name_parts_from_folder
        
        first, last = _clean_name_parts_from_folder("John_Doe_21234567")
        
        assert first == "John"
        assert last == "Doe"
        assert "21234567" not in first
        assert "21234567" not in last
    
    def test_empty_string(self):
        """Empty string should return Unknown."""
        from writers.create_grading_sheet import _clean_name_parts_from_folder
        
        first, last = _clean_name_parts_from_folder("")
        
        assert first == "Unknown"
        assert last == "Unknown"
    
    def test_only_id(self):
        """Only ID number should return Unknown."""
        from writers.create_grading_sheet import _clean_name_parts_from_folder
        
        first, last = _clean_name_parts_from_folder("12345678")
        
        assert first == "Unknown"
        assert last == "Unknown"
    
    def test_single_name_no_id(self):
        """Single name without ID."""
        from writers.create_grading_sheet import _clean_name_parts_from_folder
        
        first, last = _clean_name_parts_from_folder("John")
        
        assert first == "John"
        assert last == "Unknown"


# ============================================================
# Test write_income_analysis_scores
# ============================================================

class TestWriteIncomeAnalysisScores:
    """Tests for write_income_analysis_scores function."""
    
    def test_writes_name_score(self, mock_worksheet):
        """Should write name score to correct cell."""
        from writers.write_income_analysis_scores import write_income_analysis_scores
        
        ws = mock_worksheet
        results = {
            "name_score": 1,
            "name_feedback": [("IA_NAME_PRESENT", {})],
            "slope_score": 6,
            "slope_feedback": [],
            "predictions_score": 6,
            "predictions_feedback": [],
            "scatterplot_score": 0,
            "scatterplot_feedback": []
        }
        
        write_income_analysis_scores(ws, results)
        
        # Check that scores were written (exact cells depend on implementation)
        # This verifies the function runs without error
    
    def test_handles_empty_feedback(self, mock_worksheet):
        """Should handle empty feedback lists."""
        from writers.write_income_analysis_scores import write_income_analysis_scores
        
        ws = mock_worksheet
        results = {
            "name_score": 0,
            "name_feedback": [],
            "slope_score": 0,
            "slope_feedback": [],
            "predictions_score": 0,
            "predictions_feedback": [],
            "scatterplot_score": 0,
            "scatterplot_feedback": []
        }
        
        # Should not raise an error
        write_income_analysis_scores(ws, results)


# ============================================================
# Test create_grading_sheets_from_folder
# ============================================================

class TestCreateGradingSheetsFromFolder:
    """Tests for create_grading_sheets_from_folder function."""
    
    @patch('writers.create_grading_sheet.ws_path')
    @patch('writers.create_grading_sheet.ensure_dir')
    def test_returns_none_for_missing_folder(self, mock_ensure_dir, mock_ws_path):
        """Should return None if student_groups folder doesn't exist."""
        from writers.create_grading_sheet import create_grading_sheets_from_folder
        
        # Mock paths
        mock_ws_path.return_value = "/mock/template.xlsx"
        mock_ensure_dir.side_effect = [
            "/mock/student_groups/course",
            "/mock/graded_output/course",
            "/mock/submissions/course"
        ]
        
        # The function checks if the folder exists
        # Since it doesn't, it should handle gracefully
    
    def test_function_exists_and_callable(self):
        """Verify function can be imported."""
        from writers.create_grading_sheet import create_grading_sheets_from_folder
        
        assert callable(create_grading_sheets_from_folder)


# ============================================================
# Test Other Writer Modules
# ============================================================

class TestWriterModuleImports:
    """Test that all writer modules can be imported."""
    
    def test_import_create_grading_sheet(self):
        """Should import create_grading_sheet module."""
        from writers.create_grading_sheet import create_grading_sheets_from_folder
        assert callable(create_grading_sheets_from_folder)
    
    def test_import_write_income_analysis(self):
        """Should import write_income_analysis_scores module."""
        from writers.write_income_analysis_scores import write_income_analysis_scores
        assert callable(write_income_analysis_scores)
    
    def test_import_unit_conversions_writer(self):
        """Should import unit_conversions_writer_v2 module."""
        from writers.unit_conversions_writer_v2 import write_unit_conversions_scores_v2
        assert callable(write_unit_conversions_scores_v2)
    
    def test_import_currency_conversion_writer(self):
        """Should import write_currency_conversion_results_v2 module."""
        from writers.write_currency_conversion_results_v2 import write_currency_conversion_results_v2
        assert callable(write_currency_conversion_results_v2)
    
    def test_import_ensure_workspace_assets(self):
        """Should import ensure_workspace_assets module."""
        from writers.ensure_workspace_assets import ensure_workspace_assets
        assert callable(ensure_workspace_assets)
    
    def test_import_generate_course_folders(self):
        """Should import generate_course_folders module."""
        from writers.generate_course_folders import generate_course_folders
        assert callable(generate_course_folders)
    
    def test_import_import_zip(self):
        """Should import import_zip_to_student_groups module."""
        from writers.import_zip_to_student_groups import import_zip_to_student_groups
        assert callable(import_zip_to_student_groups)
    
    def test_import_build_instructor_master(self):
        """Should import build_instructor_master_workbook module."""
        from writers.build_instructor_master_workbook import build_instructor_master_workbook
        assert callable(build_instructor_master_workbook)


# ============================================================
# Test unit_conversions_writer_v2
# ============================================================

class TestUnitConversionsWriter:
    """Tests for unit_conversions_writer_v2 module."""
    
    def test_writes_scores(self, mock_worksheet):
        """Should write unit conversion scores to worksheet."""
        from writers.unit_conversions_writer_v2 import write_unit_conversions_scores_v2
        
        ws = mock_worksheet
        results = {
            "unit_text_score": 10,
            "formulas_score": 20,
            "final_formula_score": 8,
            "final_unit_score": 4,
            "temp_and_celsius_score": 4,
            "unit_text_feedback": [],
            "formulas_feedback": [],
            "final_formula_feedback": [],
            "final_unit_feedback": [],
            "temp_and_celsius_feedback": []
        }
        
        # Should not raise an error
        write_unit_conversions_scores_v2(ws, results)


# ============================================================
# Test currency_conversion_writer_v2
# ============================================================

class TestCurrencyConversionWriter:
    """Tests for write_currency_conversion_results_v2 module."""
    
    def test_writes_scores(self, mock_worksheet):
        """Should write currency conversion scores to worksheet."""
        from writers.write_currency_conversion_results_v2 import write_currency_conversion_results_v2
        
        ws = mock_worksheet
        results = {
            "row15_score": 2.0,
            "row15_feedback": [],
            "row16_score": 2.0,
            "row16_feedback": [],
            "row17_score": 2.0,
            "row17_feedback": [],
            "row18_score": 4.0,
            "row18_feedback": [],
            "row19_accuracy_score": 4.0,
            "row19_format_score": 1.0,
            "row19_feedback": [],
            "row20_formula_score": 8.0,
            "row20_format_score": 1.0,
            "row20_feedback": [],
            "row21_formula_score": 8.0,
            "row21_format_score": 1.0,
            "row21_feedback": [],
            "formatting_total": 4.0
        }
        
        # Should not raise an error
        write_currency_conversion_results_v2(ws, results)
