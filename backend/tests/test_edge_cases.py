"""
test_edge_cases.py — Edge case and error handling tests

Tests edge cases across all modules including:
- Empty submissions
- Corrupted files
- Partial work
- Unicode characters
- Large files
- Missing data
"""

import pytest
import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# Test Empty Submission Handling
# ============================================================

class TestEmptySubmissions:
    """Tests for handling empty or minimal submissions."""
    
    def test_income_analysis_all_empty(self, mock_worksheet):
        """Income Analysis with all empty cells."""
        from graders.income_analysis.grade_income_analysis import grade_income_analysis
        
        ws = mock_worksheet
        # Leave all cells empty
        
        results = grade_income_analysis(ws)
        
        # Should return 0 scores but not crash
        assert results["name_score"] == 0
        assert results["slope_score"] >= 0
        assert results["predictions_score"] >= 0
    
    def test_unit_conversions_all_empty(self, mock_worksheet):
        """Unit Conversions with all empty cells."""
        from graders.unit_conversions.unit_conversions_checker_v2 import grade_unit_conversions_tab_v2
        
        ws = mock_worksheet
        
        results = grade_unit_conversions_tab_v2(ws)
        
        assert results["unit_text_score"] == 0
        assert results["formulas_score"] == 0
        assert results["temp_and_celsius_score"] == 0
    
    def test_currency_conversion_all_empty(self, mock_worksheet):
        """Currency Conversion with all empty cells."""
        from graders.currency_conversion.row15_name_letters_v2 import grade_row15_name_letters_v2
        
        ws = mock_worksheet
        
        score, feedback = grade_row15_name_letters_v2(ws, "John_Doe")
        
        assert score == 0


# ============================================================
# Test Unicode and Special Characters
# ============================================================

class TestUnicodeHandling:
    """Tests for handling Unicode and special characters."""
    
    def test_name_with_accents(self, mock_worksheet):
        """Student name with accented characters."""
        from graders.income_analysis.check_name_present import check_name_present
        
        ws = mock_worksheet
        ws["B1"] = "José García"
        
        score, feedback = check_name_present(ws)
        
        assert score == 1  # Name is present
    
    def test_name_with_emoji(self, mock_worksheet):
        """Student name with emoji (should still count)."""
        from graders.income_analysis.check_name_present import check_name_present
        
        ws = mock_worksheet
        ws["B1"] = "John 🎓 Doe"
        
        score, feedback = check_name_present(ws)
        
        assert score == 1  # Name is present (emoji is just extra)
    
    def test_formula_with_unicode(self, mock_worksheet):
        """Formula validation with Unicode characters nearby."""
        from graders.income_analysis.check_slope_intercept import check_slope_intercept
        
        ws = mock_worksheet
        ws["B30"] = "=SLOPE(B19:B26,A19:A26)"
        ws["B31"] = "=INTERCEPT(B19:B26,A19:A26)"
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 6  # Formulas are correct
    
    def test_unit_with_special_characters(self, mock_worksheet):
        """Unit labels with special characters."""
        from utilities.normalizers import normalize_unit_text
        
        # Units with degree symbol (temperature)
        result = normalize_unit_text("°C/°F")
        assert isinstance(result, str)
    
    def test_country_name_with_accents(self):
        """Country name with accented characters."""
        from graders.currency_conversion.currency_lookup import get_country_entry_by_name
        
        # Test with various country names
        # Even if country not found, should not crash
        result = get_country_entry_by_name("México")
        # May return None if not in list, but shouldn't crash
        
        # Test with a known country
        result = get_country_entry_by_name("Mexico")
        assert result is not None
        assert result["currency_code"] == "MXN"


# ============================================================
# Test Partial Work Scenarios
# ============================================================

class TestPartialWork:
    """Tests for partially completed submissions."""
    
    def test_slope_only(self, mock_worksheet):
        """Only SLOPE formula filled in, INTERCEPT missing."""
        from graders.income_analysis.check_slope_intercept import check_slope_intercept
        
        ws = mock_worksheet
        ws["B30"] = "=SLOPE(B19:B26,A19:A26)"
        ws["B31"] = None
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 3  # Only slope points
    
    def test_intercept_only(self, mock_worksheet):
        """Only INTERCEPT formula filled in, SLOPE missing."""
        from graders.income_analysis.check_slope_intercept import check_slope_intercept
        
        ws = mock_worksheet
        ws["B30"] = None
        ws["B31"] = "=INTERCEPT(B19:B26,A19:A26)"
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 3  # Only intercept points
    
    def test_some_predictions_filled(self, mock_worksheet):
        """Only some prediction cells filled."""
        from graders.income_analysis.check_predictions import check_predictions
        
        ws = mock_worksheet
        
        # Fill only first 5 cells (out of 17)
        for row in range(19, 24):
            ws[f"E{row}"] = f"=B30*D{row}+B31"
        
        score, feedback = check_predictions(ws)
        
        # Score should be proportional (5/17 * 6 ≈ 1.76)
        assert 1 <= score <= 3
    
    def test_currency_partial_letters(self, mock_worksheet):
        """Only some name letters filled."""
        from graders.currency_conversion.row15_name_letters_v2 import grade_row15_name_letters_v2
        
        ws = mock_worksheet
        ws["C15"] = "J"  # Correct
        ws["D15"] = "O"  # Correct
        ws["E15"] = None  # Missing
        ws["F15"] = None  # Missing
        
        score, feedback = grade_row15_name_letters_v2(ws, "John_Doe")
        
        assert score == 1.0  # Half points
    
    def test_unit_conversions_partial(self, mock_worksheet):
        """Only some unit conversion rows filled."""
        from graders.unit_conversions.row26_checker_v2 import grade_row_26_v2
        
        ws = mock_worksheet
        # Fill only formulas, not units
        ws["F26"] = "=L14/I14"
        ws["I26"] = "=L17/I17"
        ws["G26"] = None  # Missing unit
        ws["J26"] = None  # Missing unit
        ws["O26"] = "=C26*F26*I26"
        ws["P26"] = None  # Missing final unit
        
        results = grade_row_26_v2(ws)
        
        assert results["formulas_score"] == 4  # Formulas correct
        assert results["unit_text_score"] == 0  # Units missing


# ============================================================
# Test Incorrect but Common Mistakes
# ============================================================

class TestCommonMistakes:
    """Tests for common student mistakes that should get partial credit."""
    
    def test_reversed_slope_intercept(self, mock_worksheet):
        """Reversed X/Y in both formulas - common mistake."""
        from graders.income_analysis.check_slope_intercept import check_slope_intercept
        
        ws = mock_worksheet
        ws["B30"] = "=SLOPE(A19:A26,B19:B26)"  # Reversed
        ws["B31"] = "=INTERCEPT(A19:A26,B19:B26)"  # Reversed
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 4  # Partial credit
        assert any(code == "IA_XY_DATA_SWAPPED" for code, _ in feedback)
    
    def test_using_average_instead_of_slope(self, mock_worksheet):
        """Using AVERAGE() instead of SLOPE()."""
        from graders.income_analysis.check_slope_intercept import check_slope_intercept
        
        ws = mock_worksheet
        ws["B30"] = "=AVERAGE(B19:B26)"  # Wrong function
        ws["B31"] = "=INTERCEPT(B19:B26,A19:A26)"  # Correct
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 3  # Only intercept points
    
    def test_hardcoded_slope_value(self, mock_worksheet):
        """Hardcoded value instead of formula."""
        from graders.income_analysis.check_slope_intercept import check_slope_intercept
        
        ws = mock_worksheet
        ws["B30"] = 5000  # Hardcoded value
        ws["B31"] = 30000  # Hardcoded value
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 0  # No credit for hardcoded
    
    def test_old_dates_in_currency(self, mock_worksheet):
        """Dates from last semester."""
        from graders.currency_conversion.row17_date_entries_v2 import grade_row17_date_entries_v2
        
        ws = mock_worksheet
        old_date = datetime.today() - timedelta(days=60)
        
        ws["C17"] = old_date
        ws["D17"] = old_date
        ws["E17"] = old_date
        ws["F17"] = old_date
        
        score, feedback, dates = grade_row17_date_entries_v2(ws)
        
        assert score == 0  # All dates too old


# ============================================================
# Test Boundary Conditions
# ============================================================

class TestBoundaryConditions:
    """Tests for boundary conditions in scoring."""
    
    def test_exactly_21_days_old_date(self, mock_worksheet):
        """Date exactly at 21-day boundary."""
        from graders.currency_conversion.row17_date_entries_v2 import grade_row17_date_entries_v2
        
        ws = mock_worksheet
        boundary_date = datetime.today() - timedelta(days=21)
        
        ws["C17"] = boundary_date
        ws["D17"] = boundary_date
        ws["E17"] = boundary_date
        ws["F17"] = boundary_date
        
        score, feedback, dates = grade_row17_date_entries_v2(ws)
        
        # Should be valid at exactly 21 days
        assert score == 2.0
    
    def test_22_days_old_date(self, mock_worksheet):
        """Date at 22 days (just over boundary)."""
        from graders.currency_conversion.row17_date_entries_v2 import grade_row17_date_entries_v2
        
        ws = mock_worksheet
        old_date = datetime.today() - timedelta(days=22)
        
        ws["C17"] = old_date
        ws["D17"] = old_date
        ws["E17"] = old_date
        ws["F17"] = old_date
        
        score, feedback, dates = grade_row17_date_entries_v2(ws)
        
        # Should be invalid at 22 days
        assert score == 0
    
    def test_temperature_exactly_32F_to_0C(self, mock_worksheet):
        """Freezing point conversion."""
        from graders.unit_conversions.temp_conversions_v2 import grade_temp_conversions_v2
        
        ws = mock_worksheet
        ws["A40"] = 32  # 32°F
        ws["C40"] = "=(5/9)*(A40-32)"  # Should give 0°C
        ws["C41"] = 0  # 0°C
        ws["A41"] = "=(9/5)*C41+32"  # Should give 32°F
        
        results = grade_temp_conversions_v2(ws)
        
        assert results["temp_and_celsius_score"] == 4


# ============================================================
# Test Data Type Handling
# ============================================================

class TestDataTypeHandling:
    """Tests for handling different data types in cells."""
    
    def test_integer_in_name_cell(self, mock_worksheet):
        """Integer value in name cell."""
        from graders.income_analysis.check_name_present import check_name_present
        
        ws = mock_worksheet
        ws["B1"] = 12345  # Integer, not string
        
        score, feedback = check_name_present(ws)
        
        assert score == 1  # Converts to "12345", counts as present
    
    def test_float_in_formula_cell(self, mock_worksheet):
        """Float value where formula expected."""
        from graders.income_analysis.check_slope_intercept import check_slope_intercept
        
        ws = mock_worksheet
        ws["B30"] = 5000.5
        ws["B31"] = 30000.5
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 0  # Not formulas
    
    def test_boolean_in_cell(self, mock_worksheet):
        """Boolean value in cell."""
        from utilities.normalizers import normalize_formula
        
        result = normalize_formula(True)
        assert result == "TRUE"
    
    def test_date_as_formula_value(self, mock_worksheet):
        """Date object in formula cell."""
        from utilities.normalizers import normalize_formula
        
        result = normalize_formula(datetime.today())
        # Should convert to string without error
        assert isinstance(result, str)


# ============================================================
# Test Very Long Inputs
# ============================================================

class TestLongInputs:
    """Tests for handling very long strings/values."""
    
    def test_very_long_name(self, mock_worksheet):
        """Very long student name."""
        from graders.income_analysis.check_name_present import check_name_present
        
        ws = mock_worksheet
        ws["B1"] = "A" * 10000  # Very long name
        
        score, feedback = check_name_present(ws)
        
        assert score == 1  # Still counts as present
    
    def test_very_long_formula(self, mock_worksheet):
        """Very long formula string."""
        from utilities.normalizers import normalize_formula
        
        long_formula = "=SLOPE(" + "A1:A100," * 100 + "B1:B100)"
        result = normalize_formula(long_formula)
        
        assert isinstance(result, str)
