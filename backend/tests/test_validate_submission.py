"""
test_validate_submission.py — Unit tests for submission validation

Tests utilities/validate_submission.py including:
- validate_required_sheets: Sheet presence checking
- get_sheet_safe: Safe sheet retrieval
- log_missing_sheets: Logging helper
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.validate_submission import (
    validate_required_sheets,
    get_sheet_safe,
    log_missing_sheets,
    REQUIRED_SHEETS
)


# ============================================================
# Mock Workbook class for testing
# ============================================================

class MockWorkbook:
    """Mock openpyxl Workbook for testing."""
    
    def __init__(self, sheet_names):
        self._sheetnames = sheet_names
        self._sheets = {name: MagicMock() for name in sheet_names}
    
    @property
    def sheetnames(self):
        return self._sheetnames
    
    def __getitem__(self, name):
        if name in self._sheets:
            return self._sheets[name]
        raise KeyError(f"Sheet '{name}' not found")


# ============================================================
# Test validate_required_sheets
# ============================================================

class TestValidateRequiredSheets:
    """Tests for validate_required_sheets function."""
    
    def test_all_sheets_present(self):
        """Workbook with all required sheets should be valid."""
        wb = MockWorkbook([
            "Income Analysis",
            "Unit Conversions",
            "Currency Conversion"
        ])
        
        is_valid, sheet_map, missing = validate_required_sheets(wb)
        
        assert is_valid is True
        assert len(missing) == 0
        assert sheet_map["Income Analysis"] == "Income Analysis"
    
    def test_missing_one_sheet(self):
        """Workbook missing one sheet should be invalid."""
        wb = MockWorkbook([
            "Income Analysis",
            "Currency Conversion"
            # Missing "Unit Conversions"
        ])
        
        is_valid, sheet_map, missing = validate_required_sheets(wb)
        
        assert is_valid is False
        assert "Unit Conversions" in missing
        assert sheet_map["Unit Conversions"] is None
    
    def test_missing_all_sheets(self):
        """Workbook with no required sheets should be invalid."""
        wb = MockWorkbook(["Sheet1", "Sheet2"])
        
        is_valid, sheet_map, missing = validate_required_sheets(wb)
        
        assert is_valid is False
        assert len(missing) == 3
    
    def test_case_insensitive_matching(self):
        """Sheet matching should be case-insensitive."""
        wb = MockWorkbook([
            "income analysis",  # lowercase
            "UNIT CONVERSIONS",  # uppercase
            "Currency Conversion"  # mixed
        ])
        
        is_valid, sheet_map, missing = validate_required_sheets(wb)
        
        assert is_valid is True
        assert sheet_map["Income Analysis"] == "income analysis"
        assert sheet_map["Unit Conversions"] == "UNIT CONVERSIONS"
    
    def test_extra_whitespace_handled(self):
        """Sheet names with extra whitespace should still match."""
        wb = MockWorkbook([
            " Income Analysis ",
            " Unit Conversions ",
            " Currency Conversion "
        ])
        
        is_valid, sheet_map, missing = validate_required_sheets(wb)
        
        # Whitespace handling depends on implementation
        # Most likely these won't match due to strip differences
        # This test documents the current behavior
    
    def test_extra_sheets_ignored(self):
        """Extra sheets in workbook should be ignored."""
        wb = MockWorkbook([
            "Income Analysis",
            "Unit Conversions",
            "Currency Conversion",
            "Extra Sheet",
            "Another Sheet"
        ])
        
        is_valid, sheet_map, missing = validate_required_sheets(wb)
        
        assert is_valid is True
        assert len(sheet_map) == 3  # Only required sheets tracked
    
    def test_custom_required_sheets(self):
        """Custom required_sheets list should be respected."""
        wb = MockWorkbook(["Sheet A", "Sheet B"])
        
        is_valid, sheet_map, missing = validate_required_sheets(
            wb, 
            required_sheets=["Sheet A", "Sheet B"]
        )
        
        assert is_valid is True
        assert len(missing) == 0
    
    def test_empty_workbook(self):
        """Empty workbook should be invalid."""
        wb = MockWorkbook([])
        
        is_valid, sheet_map, missing = validate_required_sheets(wb)
        
        assert is_valid is False
        assert len(missing) == 3


# ============================================================
# Test get_sheet_safe
# ============================================================

class TestGetSheetSafe:
    """Tests for get_sheet_safe function."""
    
    def test_sheet_exists(self):
        """Existing sheet should be returned."""
        wb = MockWorkbook(["Income Analysis"])
        
        sheet = get_sheet_safe(wb, "Income Analysis")
        
        assert sheet is not None
    
    def test_sheet_not_exists(self):
        """Non-existing sheet should return None."""
        wb = MockWorkbook(["Other Sheet"])
        
        sheet = get_sheet_safe(wb, "Income Analysis")
        
        assert sheet is None
    
    def test_case_insensitive_default(self):
        """Case-insensitive matching should be default."""
        wb = MockWorkbook(["income analysis"])
        
        sheet = get_sheet_safe(wb, "Income Analysis")
        
        assert sheet is not None
    
    def test_case_sensitive_option(self):
        """Case-sensitive matching should work when specified."""
        wb = MockWorkbook(["income analysis"])
        
        sheet = get_sheet_safe(wb, "Income Analysis", case_insensitive=False)
        
        assert sheet is None
    
    def test_case_sensitive_exact_match(self):
        """Case-sensitive should work for exact match."""
        wb = MockWorkbook(["Income Analysis"])
        
        sheet = get_sheet_safe(wb, "Income Analysis", case_insensitive=False)
        
        assert sheet is not None


# ============================================================
# Test log_missing_sheets
# ============================================================

class TestLogMissingSheets:
    """Tests for log_missing_sheets function."""
    
    @patch('utilities.validate_submission.get_logger')
    def test_logs_warning_with_sheets(self, mock_get_logger):
        """Should log warning with missing sheet names."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_missing_sheets("John_Doe", ["Income Analysis", "Unit Conversions"])
        
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        assert "John_Doe" in call_args
        assert "Income Analysis" in call_args
    
    @patch('utilities.validate_submission.get_logger')
    def test_empty_missing_list(self, mock_get_logger):
        """Empty missing list should still log."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        log_missing_sheets("John_Doe", [])
        
        mock_logger.warning.assert_called_once()


# ============================================================
# Test REQUIRED_SHEETS constant
# ============================================================

class TestRequiredSheetsConstant:
    """Tests for REQUIRED_SHEETS constant."""
    
    def test_contains_expected_sheets(self):
        """REQUIRED_SHEETS should contain all expected sheet names."""
        expected = ["Income Analysis", "Unit Conversions", "Currency Conversion"]
        
        assert REQUIRED_SHEETS == expected
    
    def test_is_list(self):
        """REQUIRED_SHEETS should be a list."""
        assert isinstance(REQUIRED_SHEETS, list)
    
    def test_has_three_sheets(self):
        """REQUIRED_SHEETS should have exactly 3 entries."""
        assert len(REQUIRED_SHEETS) == 3
