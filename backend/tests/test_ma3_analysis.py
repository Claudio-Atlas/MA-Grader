"""
test_ma3_analysis.py — Unit tests for MA3 Analysis tab graders

Tests cover:
- Name validation
- Difference formula validation
- Statistics formula validation (Mean, Median, StdDev, Range)
- Percentile formula validation
- Empirical rule formula validation
- Written analysis extraction
- Formatting checks
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graders.ma3_analysis.check_name import check_name
from graders.ma3_analysis.check_differences import _is_valid_difference_formula
from graders.ma3_analysis.check_statistics import (
    _check_mean_formula, _check_median_formula, 
    _check_stdev_formula, _check_range_formula
)
from graders.ma3_analysis.check_percentiles import _check_percentile_formula
from graders.ma3_analysis.check_empirical_rule import (
    _check_lower_bound_formula, _check_upper_bound_formula
)


# ============================================================
# Name Validation Tests
# ============================================================

class MockCell:
    """Simple mock for a cell."""
    def __init__(self, value):
        self.value = value

class MockSheet:
    """Simple mock for a worksheet."""
    def __init__(self, b10_value):
        self._b10_value = b10_value
    
    def __getitem__(self, key):
        if key == "B10":
            return MockCell(self._b10_value)
        return MockCell(None)


class TestNameValidation:
    """Tests for check_name function."""
    
    def test_name_present(self):
        """Valid name should score 1.0."""
        mock_sheet = MockSheet("John Smith")
        
        score, feedback = check_name(mock_sheet)
        assert score == 1.0
        assert feedback[0][0] == "NAME_PRESENT"
    
    def test_name_missing_empty(self):
        """Empty name should score 0."""
        mock_sheet = MockSheet("")
        
        score, feedback = check_name(mock_sheet)
        assert score == 0.0
        assert feedback[0][0] == "NAME_MISSING"
    
    def test_name_missing_none(self):
        """None value should score 0."""
        mock_sheet = MockSheet(None)
        
        score, feedback = check_name(mock_sheet)
        assert score == 0.0
        assert feedback[0][0] == "NAME_MISSING"
    
    def test_name_placeholder(self):
        """Placeholder text should score 0."""
        mock_sheet = MockSheet("Your Name Here")
        
        score, feedback = check_name(mock_sheet)
        assert score == 0.0
        assert feedback[0][0] == "NAME_MISSING"
    
    def test_name_too_short(self):
        """Very short name should get partial credit."""
        mock_sheet = MockSheet("AB")
        
        score, feedback = check_name(mock_sheet)
        assert score == 0.5
        assert feedback[0][0] == "NAME_TOO_SHORT"


# ============================================================
# Difference Formula Tests
# ============================================================

class TestDifferenceFormula:
    """Tests for difference formula validation."""
    
    def test_basic_difference(self):
        """Basic =C14-B14 should be valid."""
        assert _is_valid_difference_formula("=C14-B14", 14) is True
    
    def test_difference_with_dollars(self):
        """=$C$14-$B$14 should be valid."""
        assert _is_valid_difference_formula("=$C$14-$B$14", 14) is True
    
    def test_difference_with_sum(self):
        """=SUM(C14-B14) should be valid (same result)."""
        assert _is_valid_difference_formula("=SUM(C14-B14)", 14) is True
    
    def test_difference_with_parentheses(self):
        """=(C14-B14) should be valid."""
        assert _is_valid_difference_formula("=(C14-B14)", 14) is True
    
    def test_difference_wrong_row(self):
        """Wrong row reference should be invalid."""
        assert _is_valid_difference_formula("=C15-B15", 14) is False
    
    def test_difference_reversed(self):
        """=B14-C14 should be invalid (wrong direction)."""
        assert _is_valid_difference_formula("=B14-C14", 14) is False
    
    def test_difference_not_formula(self):
        """Plain number should be invalid."""
        assert _is_valid_difference_formula("5", 14) is False
    
    def test_difference_none(self):
        """None should be invalid."""
        assert _is_valid_difference_formula(None, 14) is False
    
    def test_difference_row_50(self):
        """Test middle row."""
        assert _is_valid_difference_formula("=C50-B50", 50) is True
    
    def test_difference_row_63(self):
        """Test last row."""
        assert _is_valid_difference_formula("=C63-B63", 63) is True


# ============================================================
# Statistics Formula Tests
# ============================================================

# Import partial credit constants
from graders.ma3_analysis.check_statistics import (
    CREDIT_FULL, CREDIT_RANGE_OFFSET, CREDIT_COMMA_NOT_COLON, CREDIT_NONE
)


class TestMeanFormula:
    """Tests for AVERAGE formula validation."""
    
    def test_basic_average_g(self):
        """AVERAGE for column G (Before data)."""
        assert _check_mean_formula("=AVERAGE(B14:B63)", "G") == CREDIT_FULL
    
    def test_basic_average_h(self):
        """AVERAGE for column H (After data)."""
        assert _check_mean_formula("=AVERAGE(C14:C63)", "H") == CREDIT_FULL
    
    def test_basic_average_i(self):
        """AVERAGE for column I (Difference data)."""
        assert _check_mean_formula("=AVERAGE(D14:D63)", "I") == CREDIT_FULL
    
    def test_average_with_dollars(self):
        """AVERAGE with absolute references."""
        assert _check_mean_formula("=AVERAGE($B$14:$B$63)", "G") == CREDIT_FULL
    
    def test_average_wrong_range(self):
        """AVERAGE with wrong column should fail."""
        assert _check_mean_formula("=AVERAGE(A14:A63)", "G") == CREDIT_NONE
    
    def test_not_average(self):
        """Non-AVERAGE function should fail."""
        assert _check_mean_formula("=SUM(B14:B63)", "G") == CREDIT_NONE
    
    # Partial credit tests
    def test_average_comma_instead_of_colon(self):
        """Using comma instead of colon should get 50% credit."""
        assert _check_mean_formula("=AVERAGE(B14,B63)", "G") == CREDIT_COMMA_NOT_COLON
    
    def test_average_comma_with_dollars(self):
        """Comma instead of colon with dollar signs."""
        assert _check_mean_formula("=AVERAGE($B$14,$B$63)", "G") == CREDIT_COMMA_NOT_COLON
    
    def test_average_range_offset_by_1(self):
        """Range off by 1 row (drag-fill error) should get 75% credit."""
        assert _check_mean_formula("=AVERAGE(B15:B64)", "G") == CREDIT_RANGE_OFFSET
    
    def test_average_range_offset_by_2(self):
        """Range off by 2 rows should get 75% credit."""
        assert _check_mean_formula("=AVERAGE(B16:B65)", "G") == CREDIT_RANGE_OFFSET
    
    def test_average_range_offset_by_3(self):
        """Range off by 3 rows should get 75% credit."""
        assert _check_mean_formula("=AVERAGE(B17:B66)", "G") == CREDIT_RANGE_OFFSET
    
    def test_average_range_offset_too_far(self):
        """Range off by more than 3 rows should get 0 credit."""
        assert _check_mean_formula("=AVERAGE(B20:B69)", "G") == CREDIT_NONE


class TestMedianFormula:
    """Tests for MEDIAN formula validation."""
    
    def test_basic_median(self):
        """Basic MEDIAN formula."""
        assert _check_median_formula("=MEDIAN(B14:B63)", "G") == CREDIT_FULL
    
    def test_median_with_dollars(self):
        """MEDIAN with absolute references."""
        assert _check_median_formula("=MEDIAN($D$14:$D$63)", "I") == CREDIT_FULL
    
    def test_not_median(self):
        """Non-MEDIAN function should fail."""
        assert _check_median_formula("=AVERAGE(B14:B63)", "G") == CREDIT_NONE
    
    # Partial credit tests
    def test_median_comma_instead_of_colon(self):
        """Using comma instead of colon should get 50% credit."""
        assert _check_median_formula("=MEDIAN(B14,B63)", "G") == CREDIT_COMMA_NOT_COLON
    
    def test_median_range_offset(self):
        """Range off by 1 row should get 75% credit."""
        assert _check_median_formula("=MEDIAN(B15:B64)", "G") == CREDIT_RANGE_OFFSET


class TestStdevFormula:
    """Tests for STDEV formula validation."""
    
    def test_stdev_basic(self):
        """Basic STDEV formula."""
        assert _check_stdev_formula("=STDEV(D14:D63)", "I") == CREDIT_FULL
    
    def test_stdev_p(self):
        """STDEV.P formula."""
        assert _check_stdev_formula("=STDEV.P(D14:D63)", "I") == CREDIT_FULL
    
    def test_stdev_s(self):
        """STDEV.S formula."""
        assert _check_stdev_formula("=STDEV.S(D14:D63)", "I") == CREDIT_FULL
    
    def test_stdev_with_xlfn(self):
        """Excel internal format with _xlfn prefix."""
        assert _check_stdev_formula("=_xlfn.STDEV.S(D14:D63)", "I") == CREDIT_FULL
    
    def test_stdev_negative(self):
        """STDEV with negative sign prefix."""
        assert _check_stdev_formula("=-STDEV.S(D14:D63)", "I") == CREDIT_FULL
    
    def test_stdev_negative_xlfn(self):
        """Negative STDEV with _xlfn prefix."""
        assert _check_stdev_formula("=-_xlfn.STDEV.S(D14:D63)", "I") == CREDIT_FULL
    
    def test_stdev_wrong_column(self):
        """STDEV with wrong column reference."""
        assert _check_stdev_formula("=STDEV.S(A14:A63)", "I") == CREDIT_NONE
    
    # Partial credit tests
    def test_stdev_comma_instead_of_colon(self):
        """Using comma instead of colon should get 50% credit."""
        assert _check_stdev_formula("=STDEV.S(D14,D63)", "I") == CREDIT_COMMA_NOT_COLON
    
    def test_stdev_range_offset(self):
        """Range off by 1 row should get 75% credit."""
        assert _check_stdev_formula("=STDEV.S(D15:D64)", "I") == CREDIT_RANGE_OFFSET


class TestRangeFormula:
    """Tests for Range (MAX-MIN) formula validation."""
    
    def test_basic_range(self):
        """Basic MAX-MIN formula."""
        assert _check_range_formula("=MAX(B14:B63)-MIN(B14:B63)", "G") == CREDIT_FULL
    
    def test_range_parentheses(self):
        """Range with parentheses."""
        assert _check_range_formula("=(MAX(D14:D63)-MIN(D14:D63))", "I") == CREDIT_FULL
    
    def test_range_missing_max(self):
        """Formula without MAX should fail."""
        assert _check_range_formula("=MIN(B14:B63)", "G") == CREDIT_NONE
    
    def test_range_missing_min(self):
        """Formula without MIN should fail."""
        assert _check_range_formula("=MAX(B14:B63)", "G") == CREDIT_NONE
    
    # Partial credit tests
    def test_range_comma_instead_of_colon(self):
        """Using comma instead of colon in MAX-MIN should get 50% credit."""
        assert _check_range_formula("=MAX(B14,B63)-MIN(B14,B63)", "G") == CREDIT_COMMA_NOT_COLON
    
    def test_range_offset(self):
        """Range off by 1 row should get 75% credit."""
        assert _check_range_formula("=MAX(B15:B64)-MIN(B15:B64)", "G") == CREDIT_RANGE_OFFSET


# ============================================================
# Percentile Formula Tests
# ============================================================

class TestPercentileFormula:
    """Tests for PERCENTILE formula validation."""
    
    def test_percentile_basic(self):
        """Basic PERCENTILE formula."""
        assert _check_percentile_formula("=PERCENTILE(D14:D63,0.5)") is True
    
    def test_percentile_inc(self):
        """PERCENTILE.INC formula."""
        assert _check_percentile_formula("=PERCENTILE.INC(D14:D63,0.47)") is True
    
    def test_percentile_exc(self):
        """PERCENTILE.EXC formula."""
        assert _check_percentile_formula("=PERCENTILE.EXC(D14:D63,0.25)") is True
    
    def test_percentile_xlfn(self):
        """Excel internal format."""
        assert _check_percentile_formula("=_xlfn.PERCENTILE.INC(D14:D63,0.49)") is True
    
    def test_percentile_wrong_range(self):
        """Wrong data range should fail."""
        assert _check_percentile_formula("=PERCENTILE(A1:A10,0.5)") is False
    
    def test_not_percentile(self):
        """Non-PERCENTILE function should fail."""
        assert _check_percentile_formula("=AVERAGE(D14:D63)") is False


# ============================================================
# Empirical Rule Formula Tests
# ============================================================

class TestEmpiricalRule:
    """Tests for empirical rule formulas."""
    
    def test_lower_bound_basic(self):
        """Basic lower bound formula."""
        assert _check_lower_bound_formula("=I18-I20") is True
    
    def test_lower_bound_dollars(self):
        """Lower bound with absolute references."""
        assert _check_lower_bound_formula("=$I$18-$I$20") is True
    
    def test_lower_bound_parentheses(self):
        """Lower bound with parentheses."""
        assert _check_lower_bound_formula("=(I18-I20)") is True
    
    def test_upper_bound_basic(self):
        """Basic upper bound formula."""
        assert _check_upper_bound_formula("=I18+I20") is True
    
    def test_upper_bound_dollars(self):
        """Upper bound with absolute references."""
        assert _check_upper_bound_formula("=$I$18+$I$20") is True
    
    def test_lower_wrong_cells(self):
        """Wrong cell references should fail."""
        assert _check_lower_bound_formula("=I17-I19") is False
    
    def test_upper_subtraction(self):
        """Subtraction instead of addition should fail."""
        assert _check_upper_bound_formula("=I18-I20") is False


# ============================================================
# Integration Tests with Real Workbook
# ============================================================

class TestRealWorkbook:
    """Integration tests using actual student submission."""
    
    @pytest.fixture
    def student_workbook(self):
        """Load a real student workbook for testing."""
        from openpyxl import load_workbook
        
        test_path = "/tmp/ma3-test/Major Assignment 3 - Online/Alvaro_Salcedo_21271090"
        if not os.path.exists(test_path):
            pytest.skip("Test data not available")
        
        xlsx_files = [f for f in os.listdir(test_path) if f.endswith('.xlsx')]
        if not xlsx_files:
            pytest.skip("No xlsx file found")
        
        wb = load_workbook(os.path.join(test_path, xlsx_files[0]), data_only=False)
        yield wb
        wb.close()
    
    def test_full_analysis_grading(self, student_workbook):
        """Test complete Analysis tab grading."""
        from graders.ma3_analysis import grade_analysis_tab
        
        ws = student_workbook["Analysis"]
        results = grade_analysis_tab(ws, "Alvaro_Salcedo")
        
        # Alvaro should have high scores
        assert results["name_score"] == 1.0
        assert results["diff_score"] == 6.0
        assert results["stats_score"] == 24.0
        assert results["percentile_score"] == 6.0
        assert results["empirical_score"] == 6.0
        # Written is always 0 (manual grading)
        assert results["written_score"] == 0.0
    
    def test_analysis_total_score(self, student_workbook):
        """Test that Analysis total is calculated correctly."""
        from graders.ma3_analysis import grade_analysis_tab
        
        ws = student_workbook["Analysis"]
        results = grade_analysis_tab(ws, "Alvaro_Salcedo")
        
        total = sum(v for k, v in results.items() 
                   if 'score' in k and isinstance(v, (int, float)))
        
        # Should be close to max (49/54 based on our test)
        assert total >= 45.0
        assert total <= 54.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
