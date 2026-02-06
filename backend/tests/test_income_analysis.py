"""
test_income_analysis.py — Unit tests for Income Analysis grading

Tests all grading functions in graders/income_analysis/ including:
- check_name_present: Name presence validation
- check_slope_intercept: SLOPE/INTERCEPT formula validation
- check_predictions: Prediction formula validation
- grade_income_analysis: Main orchestrator
"""

import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graders.income_analysis.check_name_present import check_name_present
from graders.income_analysis.check_slope_intercept import check_slope_intercept
from graders.income_analysis.check_predictions import check_predictions, _has_required_refs, _has_years_ref
from graders.income_analysis.grade_income_analysis import grade_income_analysis


# ============================================================
# Test check_name_present
# ============================================================

class TestCheckNamePresent:
    """Tests for name presence checking."""
    
    def test_name_present(self, mock_worksheet):
        """Name present should score 1 point."""
        ws = mock_worksheet
        ws["B1"] = "John Doe"
        
        score, feedback = check_name_present(ws)
        
        assert score == 1
        assert any(code == "IA_NAME_PRESENT" for code, _ in feedback)
    
    def test_name_missing(self, mock_worksheet):
        """Missing name should score 0 points."""
        ws = mock_worksheet
        ws["B1"] = None
        
        score, feedback = check_name_present(ws)
        
        assert score == 0
        assert any(code == "IA_NAME_MISSING" for code, _ in feedback)
    
    def test_name_empty_string(self, mock_worksheet):
        """Empty string should score 0 points."""
        ws = mock_worksheet
        ws["B1"] = ""
        
        score, feedback = check_name_present(ws)
        
        assert score == 0
    
    def test_name_whitespace_only(self, mock_worksheet):
        """Whitespace-only should score 0 points."""
        ws = mock_worksheet
        ws["B1"] = "   "
        
        score, feedback = check_name_present(ws)
        
        assert score == 0
    
    def test_name_numeric(self, mock_worksheet):
        """Numeric value should be accepted (converted to string)."""
        ws = mock_worksheet
        ws["B1"] = 12345
        
        score, feedback = check_name_present(ws)
        
        assert score == 1  # "12345" is non-empty
    
    def test_name_single_char(self, mock_worksheet):
        """Single character should be accepted."""
        ws = mock_worksheet
        ws["B1"] = "J"
        
        score, feedback = check_name_present(ws)
        
        assert score == 1


# ============================================================
# Test check_slope_intercept
# ============================================================

class TestCheckSlopeIntercept:
    """Tests for slope and intercept formula checking."""
    
    def test_both_correct(self, mock_worksheet):
        """Both correct formulas should score 6 points."""
        ws = mock_worksheet
        ws["B30"] = "=SLOPE(B19:B26,A19:A26)"
        ws["B31"] = "=INTERCEPT(B19:B26,A19:A26)"
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 6
        assert any(code == "IA_SLOPE_CORRECT" for code, _ in feedback)
        assert any(code == "IA_INTERCEPT_CORRECT" for code, _ in feedback)
    
    def test_both_correct_with_absolute_refs(self, mock_worksheet):
        """Formulas with $ (absolute refs) should still be correct."""
        ws = mock_worksheet
        ws["B30"] = "=$SLOPE($B$19:$B$26,$A$19:$A$26)"
        ws["B31"] = "=$INTERCEPT($B$19:$B$26,$A$19:$A$26)"
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 6
    
    def test_both_correct_lowercase(self, mock_worksheet):
        """Lowercase formulas should be accepted."""
        ws = mock_worksheet
        ws["B30"] = "=slope(b19:b26,a19:a26)"
        ws["B31"] = "=intercept(b19:b26,a19:a26)"
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 6
    
    def test_both_reversed(self, mock_worksheet):
        """Both reversed X/Y should score 4 points (partial)."""
        ws = mock_worksheet
        ws["B30"] = "=SLOPE(A19:A26,B19:B26)"
        ws["B31"] = "=INTERCEPT(A19:A26,B19:B26)"
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 4
        assert any(code == "IA_SLOPE_REVERSED" for code, _ in feedback)
        assert any(code == "IA_INTERCEPT_REVERSED" for code, _ in feedback)
        assert any(code == "IA_XY_DATA_SWAPPED" for code, _ in feedback)
    
    def test_one_correct_one_reversed(self, mock_worksheet):
        """One correct, one reversed should score 5 points."""
        ws = mock_worksheet
        ws["B30"] = "=SLOPE(B19:B26,A19:A26)"  # Correct
        ws["B31"] = "=INTERCEPT(A19:A26,B19:B26)"  # Reversed
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 5
    
    def test_wrong_ranges(self, mock_worksheet):
        """Using SLOPE/INTERCEPT with wrong ranges should score 2 points."""
        ws = mock_worksheet
        ws["B30"] = "=SLOPE(C1:C10,D1:D10)"  # Wrong ranges
        ws["B31"] = "=INTERCEPT(C1:C10,D1:D10)"  # Wrong ranges
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 2  # 1 point each for using correct function
        assert any(code == "IA_SLOPE_WRONG_RANGE" for code, _ in feedback)
        assert any(code == "IA_INTERCEPT_WRONG_RANGE" for code, _ in feedback)
    
    def test_missing_formulas(self, mock_worksheet):
        """Missing formulas should score 0 points."""
        ws = mock_worksheet
        ws["B30"] = None
        ws["B31"] = None
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 0
        assert any(code == "IA_SLOPE_MISSING" for code, _ in feedback)
        assert any(code == "IA_INTERCEPT_MISSING" for code, _ in feedback)
    
    def test_hardcoded_values(self, mock_worksheet):
        """Hardcoded values instead of formulas should score 0."""
        ws = mock_worksheet
        ws["B30"] = 5000  # Hardcoded value
        ws["B31"] = 30000  # Hardcoded value
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 0
    
    def test_wrong_functions(self, mock_worksheet):
        """Using wrong functions should score 0."""
        ws = mock_worksheet
        ws["B30"] = "=AVERAGE(B19:B26)"  # Wrong function
        ws["B31"] = "=SUM(B19:B26)"  # Wrong function
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 0
    
    def test_spaces_in_formula(self, mock_worksheet):
        """Formulas with spaces should be normalized and accepted."""
        ws = mock_worksheet
        ws["B30"] = "= SLOPE( B19:B26 , A19:A26 )"
        ws["B31"] = "= INTERCEPT( B19:B26 , A19:A26 )"
        
        score, feedback = check_slope_intercept(ws)
        
        assert score == 6


# ============================================================
# Test _has_required_refs helper
# ============================================================

class TestHasRequiredRefs:
    """Tests for _has_required_refs helper function."""
    
    def test_has_both_refs(self):
        """Formula with both B30 and B31 should return True."""
        assert _has_required_refs("=B30*D19+B31") is True
    
    def test_has_both_refs_absolute(self):
        """Formula with absolute refs should return True."""
        assert _has_required_refs("=$B$30*D19+$B$31") is True
    
    def test_missing_b30(self):
        """Formula missing B30 should return False."""
        assert _has_required_refs("=5000*D19+B31") is False
    
    def test_missing_b31(self):
        """Formula missing B31 should return False."""
        assert _has_required_refs("=B30*D19+30000") is False
    
    def test_missing_both(self):
        """Formula missing both refs should return False."""
        assert _has_required_refs("=5000*D19+30000") is False
    
    def test_empty_formula(self):
        """Empty formula should return False."""
        assert _has_required_refs("") is False
        assert _has_required_refs(None) is False
    
    def test_case_insensitive(self):
        """Check should be case-insensitive."""
        assert _has_required_refs("=b30*d19+b31") is True


# ============================================================
# Test _has_years_ref helper
# ============================================================

class TestHasYearsRef:
    """Tests for _has_years_ref helper function."""
    
    def test_correct_row(self):
        """Formula with correct D{row} should return True."""
        assert _has_years_ref("=B30*D19+B31", 19) is True
        assert _has_years_ref("=B30*D25+B31", 25) is True
    
    def test_wrong_row(self):
        """Formula with wrong D{row} should return False."""
        assert _has_years_ref("=B30*D19+B31", 20) is False
        assert _has_years_ref("=B30*D25+B31", 19) is False
    
    def test_absolute_ref(self):
        """Absolute reference should work."""
        assert _has_years_ref("=B30*$D$19+B31", 19) is True
    
    def test_empty_formula(self):
        """Empty formula should return False."""
        assert _has_years_ref("", 19) is False
        assert _has_years_ref(None, 19) is False


# ============================================================
# Test check_predictions
# ============================================================

class TestCheckPredictions:
    """Tests for prediction formula checking."""
    
    def test_all_correct(self, mock_worksheet):
        """All 17 correct prediction formulas should score 6.0."""
        ws = mock_worksheet
        
        # Set up all prediction formulas (E19:E35)
        for row in range(19, 36):
            ws[f"E{row}"] = f"=B30*D{row}+B31"
        
        score, feedback = check_predictions(ws)
        
        assert score == 6.0
        assert any(code == "IA_PREDICTIONS_ALL_CORRECT" for code, _ in feedback)
    
    def test_all_correct_with_absolute_refs(self, mock_worksheet):
        """Formulas with absolute refs should be correct."""
        ws = mock_worksheet
        
        for row in range(19, 36):
            ws[f"E{row}"] = f"=$B$30*$D${row}+$B$31"
        
        score, feedback = check_predictions(ws)
        
        assert score == 6.0
    
    def test_partial_correct(self, mock_worksheet):
        """Partial correct should score proportionally."""
        ws = mock_worksheet
        
        # Set 8 correct formulas (approximately half)
        for row in range(19, 27):  # 8 rows
            ws[f"E{row}"] = f"=B30*D{row}+B31"
        
        # Set 9 incorrect formulas
        for row in range(27, 36):  # 9 rows
            ws[f"E{row}"] = "=INVALID"
        
        score, feedback = check_predictions(ws)
        
        # Score should be approximately (8/17) * 6 ≈ 2.8
        assert 2.5 <= score <= 3.5
        assert any(code == "IA_PREDICTIONS_PARTIAL" for code, _ in feedback)
    
    def test_none_correct_not_formulas(self, mock_worksheet):
        """No formulas (hardcoded values) should score 0."""
        ws = mock_worksheet
        
        for row in range(19, 36):
            ws[f"E{row}"] = 50000  # Hardcoded value
        
        score, feedback = check_predictions(ws)
        
        assert score == 0.0
        assert any(code == "IA_PREDICTIONS_NOT_FORMULAS" for code, _ in feedback)
    
    def test_missing_slope_intercept_refs(self, mock_worksheet):
        """Formulas missing B30/B31 refs should score 0."""
        ws = mock_worksheet
        
        for row in range(19, 36):
            ws[f"E{row}"] = f"=5000*D{row}+30000"  # Hardcoded slope/intercept
        
        score, feedback = check_predictions(ws)
        
        assert score == 0.0
        assert any(code == "IA_PREDICTIONS_MISSING_REFS" for code, _ in feedback)
    
    def test_missing_years_ref(self, mock_worksheet):
        """Formulas missing D column refs should score 0."""
        ws = mock_worksheet
        
        for row in range(19, 36):
            ws[f"E{row}"] = "=B30*5+B31"  # Hardcoded years
        
        score, feedback = check_predictions(ws)
        
        assert score == 0.0
        assert any(code == "IA_PREDICTIONS_MISSING_YEARS" for code, _ in feedback)
    
    def test_empty_cells(self, mock_worksheet):
        """Empty cells should score 0."""
        ws = mock_worksheet
        
        # Leave all cells empty (None)
        for row in range(19, 36):
            ws[f"E{row}"] = None
        
        score, feedback = check_predictions(ws)
        
        assert score == 0.0


# ============================================================
# Test grade_income_analysis (Orchestrator)
# ============================================================

class TestGradeIncomeAnalysis:
    """Tests for the main income analysis grading orchestrator."""
    
    def test_perfect_score(self, income_analysis_worksheet):
        """Perfect submission should score maximum points."""
        ws = income_analysis_worksheet
        
        results = grade_income_analysis(ws)
        
        assert results["name_score"] == 1
        assert results["slope_score"] == 6 + 1  # 6 formulas + 1 formatting (if implemented)
        # Note: Actual score depends on formatting check implementation
        assert results["scatterplot_score"] == 0  # Always manual
    
    def test_returns_all_keys(self, mock_worksheet):
        """Results should contain all expected keys."""
        ws = mock_worksheet
        ws["B1"] = "Test"
        ws["B30"] = "=SLOPE(B19:B26,A19:A26)"
        ws["B31"] = "=INTERCEPT(B19:B26,A19:A26)"
        
        results = grade_income_analysis(ws)
        
        assert "name_score" in results
        assert "name_feedback" in results
        assert "slope_score" in results
        assert "slope_feedback" in results
        assert "predictions_score" in results
        assert "predictions_feedback" in results
        assert "scatterplot_score" in results
        assert "scatterplot_feedback" in results
    
    def test_scatterplot_always_manual(self, mock_worksheet):
        """Scatterplot should always return 0 score (manual grading)."""
        ws = mock_worksheet
        
        results = grade_income_analysis(ws)
        
        assert results["scatterplot_score"] == 0
        assert any(code == "IA_SCATTER_NOT_CHECKED" for code, _ in results["scatterplot_feedback"])
    
    def test_feedback_format(self, mock_worksheet):
        """All feedback should be list of (code, params) tuples."""
        ws = mock_worksheet
        ws["B1"] = "Test"
        
        results = grade_income_analysis(ws)
        
        for key in ["name_feedback", "slope_feedback", "predictions_feedback", "scatterplot_feedback"]:
            feedback = results[key]
            assert isinstance(feedback, list)
            for item in feedback:
                assert isinstance(item, tuple)
                assert len(item) == 2
                code, params = item
                assert isinstance(code, str)
                assert isinstance(params, dict)
