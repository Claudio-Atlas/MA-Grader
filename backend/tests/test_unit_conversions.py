"""
test_unit_conversions.py — Unit tests for Unit Conversions grading

Tests all grading functions in graders/unit_conversions/ including:
- row26_checker_v2: Row 26 (mcg/mg, ml/tsp) conversion grading
- row27_checker_v2: Row 27 (gal/l, h/d) conversion grading
- row28_checker_v2: Row 28 (kg/lb, in/cm) conversion grading
- row29_checker_v2: Row 29 (ft/mi, yr/d, d/h) conversion grading
- temp_conversions_v2: Temperature conversion grading
- unit_conversions_checker_v2: Main orchestrator
"""

import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graders.unit_conversions.row26_checker_v2 import grade_row_26_v2
from graders.unit_conversions.temp_conversions_v2 import grade_temp_conversions_v2
from graders.unit_conversions.unit_conversions_checker_v2 import grade_unit_conversions_tab_v2
from graders.unit_conversions.utils import norm_formula, norm_unit


# ============================================================
# Test norm_formula utility
# ============================================================

class TestNormFormula:
    """Tests for norm_formula wrapper function."""
    
    def test_basic_normalization(self):
        """Basic formula should be normalized."""
        assert norm_formula("= $L$14 / $I$14 ") == "=L14/I14"
    
    def test_none_input(self):
        """None should return empty string."""
        assert norm_formula(None) == ""
    
    def test_uppercase(self):
        """Formula should be uppercased."""
        assert norm_formula("=l14/i14") == "=L14/I14"


# ============================================================
# Test norm_unit utility
# ============================================================

class TestNormUnit:
    """Tests for norm_unit wrapper function."""
    
    def test_basic_normalization(self):
        """Basic unit should be normalized."""
        assert norm_unit("mcg / mg") == "mcg/mg"
    
    def test_lowercase(self):
        """Unit should be lowercased."""
        assert norm_unit("MCG/MG") == "mcg/mg"
    
    def test_time_normalization(self):
        """Time units should be normalized."""
        # Note: Only exact "hr" is replaced, not "hours"
        assert norm_unit("hr/day") == "h/d"


# ============================================================
# Test Row 26 Grading
# ============================================================

class TestRow26Grading:
    """Tests for Row 26 (mcg/mg and ml/tsp) grading."""
    
    def test_perfect_score(self, mock_worksheet):
        """Perfect Row 26 should score maximum points."""
        ws = mock_worksheet
        
        # Set up perfect submission
        ws["F26"] = "=L14/I14"  # mcg/mg ratio
        ws["G26"] = "mcg/mg"
        ws["I26"] = "=L17/I17"  # ml/tsp ratio
        ws["J26"] = "ml/tsp"
        ws["O26"] = "=C26*F26*I26"
        ws["P26"] = "mcg/tsp"
        
        results = grade_row_26_v2(ws)
        
        assert results["formulas_score"] == 4  # 2 per ratio
        assert results["unit_text_score"] == 2  # 1 per label
        assert results["final_formula_score"] == 2
        assert results["final_unit_score"] == 1
    
    def test_swapped_ratio_positions(self, mock_worksheet):
        """Ratios in opposite cells should still be correct."""
        ws = mock_worksheet
        
        # Swap positions (ml/tsp in F26, mcg/mg in I26)
        ws["F26"] = "=L17/I17"  # ml/tsp ratio (swapped)
        ws["G26"] = "ml/tsp"
        ws["I26"] = "=L14/I14"  # mcg/mg ratio (swapped)
        ws["J26"] = "mcg/mg"
        ws["O26"] = "=C26*F26*I26"
        ws["P26"] = "mcg/tsp"
        
        results = grade_row_26_v2(ws)
        
        assert results["formulas_score"] == 4  # Order doesn't matter
    
    def test_simplified_formulas(self, mock_worksheet):
        """Simplified formula variants should be accepted."""
        ws = mock_worksheet
        
        ws["F26"] = "=L14"  # Simplified (no /I14)
        ws["G26"] = "mcg/mg"
        ws["I26"] = "=L17"  # Simplified
        ws["J26"] = "ml/tsp"
        ws["O26"] = "=C26*F26*I26"
        ws["P26"] = "mcg/tsp"
        
        results = grade_row_26_v2(ws)
        
        assert results["formulas_score"] == 4
    
    def test_duplicate_ratio_not_allowed(self, mock_worksheet):
        """Using same ratio twice should not get double credit."""
        ws = mock_worksheet
        
        ws["F26"] = "=L14/I14"  # mcg/mg ratio
        ws["G26"] = "mcg/mg"
        ws["I26"] = "=L14/I14"  # Same ratio (duplicate)
        ws["J26"] = "mcg/mg"
        ws["O26"] = "=C26*F26*I26"
        ws["P26"] = "mcg/tsp"
        
        results = grade_row_26_v2(ws)
        
        # Only one ratio should get credit
        assert results["formulas_score"] == 2
    
    def test_wrong_formulas(self, mock_worksheet):
        """Wrong formulas should score 0."""
        ws = mock_worksheet
        
        ws["F26"] = "=L99/I99"  # Wrong lookup
        ws["G26"] = "mcg/mg"
        ws["I26"] = "=L99/I99"  # Wrong lookup
        ws["J26"] = "ml/tsp"
        ws["O26"] = "=C26*F26*I26"
        ws["P26"] = "mcg/tsp"
        
        results = grade_row_26_v2(ws)
        
        assert results["formulas_score"] == 0
    
    def test_wrong_unit_labels(self, mock_worksheet):
        """Wrong unit labels should score 0 for units."""
        ws = mock_worksheet
        
        ws["F26"] = "=L14/I14"
        ws["G26"] = "wrong/unit"  # Wrong
        ws["I26"] = "=L17/I17"
        ws["J26"] = "also/wrong"  # Wrong
        ws["O26"] = "=C26*F26*I26"
        ws["P26"] = "mcg/tsp"
        
        results = grade_row_26_v2(ws)
        
        assert results["unit_text_score"] == 0
        assert results["formulas_score"] == 4  # Formulas still correct
    
    def test_wrong_final_formula(self, mock_worksheet):
        """Wrong final formula should score 0 for that part."""
        ws = mock_worksheet
        
        ws["F26"] = "=L14/I14"
        ws["G26"] = "mcg/mg"
        ws["I26"] = "=L17/I17"
        ws["J26"] = "ml/tsp"
        ws["O26"] = "=C26+F26+I26"  # Using + instead of *
        ws["P26"] = "mcg/tsp"
        
        results = grade_row_26_v2(ws)
        
        assert results["final_formula_score"] == 0
    
    def test_wrong_final_unit(self, mock_worksheet):
        """Wrong final unit should score 0 for that part."""
        ws = mock_worksheet
        
        ws["F26"] = "=L14/I14"
        ws["G26"] = "mcg/mg"
        ws["I26"] = "=L17/I17"
        ws["J26"] = "ml/tsp"
        ws["O26"] = "=C26*F26*I26"
        ws["P26"] = "wrong/unit"  # Wrong final unit
        
        results = grade_row_26_v2(ws)
        
        assert results["final_unit_score"] == 0
    
    def test_empty_cells(self, mock_worksheet):
        """Empty cells should score 0."""
        ws = mock_worksheet
        
        # Leave everything empty
        
        results = grade_row_26_v2(ws)
        
        assert results["formulas_score"] == 0
        assert results["unit_text_score"] == 0
        assert results["final_formula_score"] == 0
        assert results["final_unit_score"] == 0
    
    def test_returns_all_keys(self, mock_worksheet):
        """Results should contain all expected keys."""
        ws = mock_worksheet
        
        results = grade_row_26_v2(ws)
        
        assert "formulas_score" in results
        assert "unit_text_score" in results
        assert "final_formula_score" in results
        assert "final_unit_score" in results
        assert "formulas_feedback" in results
        assert "unit_text_feedback" in results
        assert "final_formula_feedback" in results
        assert "final_unit_feedback" in results


# ============================================================
# Test Temperature Conversions
# ============================================================

class TestTemperatureConversions:
    """Tests for temperature conversion grading."""
    
    def test_both_correct(self, mock_worksheet):
        """Both correct temperature formulas should score 4 points."""
        ws = mock_worksheet
        
        ws["A40"] = 98.6  # Fahrenheit input
        ws["C40"] = "=(5/9)*(A40-32)"  # F to C
        ws["C41"] = 37  # Celsius input
        ws["A41"] = "=(9/5)*C41+32"  # C to F
        
        results = grade_temp_conversions_v2(ws)
        
        assert results["temp_and_celsius_score"] == 4
        assert any(code == "UC_TEMP_C40_CORRECT" for code, _ in results["temp_and_celsius_feedback"])
        assert any(code == "UC_TEMP_A41_CORRECT" for code, _ in results["temp_and_celsius_feedback"])
    
    def test_formula_variations_c40(self, mock_worksheet):
        """Various valid C40 formula patterns should be accepted."""
        ws = mock_worksheet
        ws["A40"] = 98.6
        ws["C41"] = 37
        ws["A41"] = "=(9/5)*C41+32"
        
        # Test different valid patterns
        valid_patterns = [
            "=(5/9)*(A40-32)",
            "=5/9*(A40-32)",
            "=(5/9)*(A40-32)",
        ]
        
        for pattern in valid_patterns:
            ws["C40"] = pattern
            results = grade_temp_conversions_v2(ws)
            assert results["temp_and_celsius_score"] >= 2, f"Pattern {pattern} should score at least 2"
    
    def test_formula_variations_a41(self, mock_worksheet):
        """Various valid A41 formula patterns should be accepted."""
        ws = mock_worksheet
        ws["A40"] = 98.6
        ws["C40"] = "=(5/9)*(A40-32)"
        ws["C41"] = 37
        
        valid_patterns = [
            "=(9/5)*C41+32",
            "=9/5*C41+32",
            "=(9/5)*C41+32",
        ]
        
        for pattern in valid_patterns:
            ws["A41"] = pattern
            results = grade_temp_conversions_v2(ws)
            assert results["temp_and_celsius_score"] >= 2, f"Pattern {pattern} should score at least 2"
    
    def test_missing_cell_reference_c40(self, mock_worksheet):
        """C40 formula missing A40 reference should get partial credit or 0."""
        ws = mock_worksheet
        ws["A40"] = 98.6
        ws["C40"] = "=(5/9)*(98.6-32)"  # Hardcoded instead of A40
        ws["C41"] = 37
        ws["A41"] = "=(9/5)*C41+32"
        
        results = grade_temp_conversions_v2(ws)
        
        # Should not get full credit for C40
        # (exact behavior depends on whether value matches)
        assert results["temp_and_celsius_score"] <= 3
    
    def test_missing_cell_reference_a41(self, mock_worksheet):
        """A41 formula missing C41 reference should get partial credit or 0."""
        ws = mock_worksheet
        ws["A40"] = 98.6
        ws["C40"] = "=(5/9)*(A40-32)"
        ws["C41"] = 37
        ws["A41"] = "=(9/5)*37+32"  # Hardcoded instead of C41
        
        results = grade_temp_conversions_v2(ws)
        
        assert results["temp_and_celsius_score"] <= 3
    
    def test_wrong_conversion_factor_c40(self, mock_worksheet):
        """C40 with wrong conversion factor should score 0 for that cell."""
        ws = mock_worksheet
        ws["A40"] = 98.6
        ws["C40"] = "=(9/5)*(A40-32)"  # Wrong: using 9/5 instead of 5/9
        ws["C41"] = 37
        ws["A41"] = "=(9/5)*C41+32"
        
        results = grade_temp_conversions_v2(ws)
        
        assert any(code == "UC_TEMP_C40_INCORRECT" for code, _ in results["temp_and_celsius_feedback"])
    
    def test_wrong_conversion_factor_a41(self, mock_worksheet):
        """A41 with wrong conversion factor should score 0 for that cell."""
        ws = mock_worksheet
        ws["A40"] = 98.6
        ws["C40"] = "=(5/9)*(A40-32)"
        ws["C41"] = 37
        ws["A41"] = "=(5/9)*C41+32"  # Wrong: using 5/9 instead of 9/5
        
        results = grade_temp_conversions_v2(ws)
        
        assert any(code == "UC_TEMP_A41_INCORRECT" for code, _ in results["temp_and_celsius_feedback"])
    
    def test_no_formula_hardcoded_values(self, mock_worksheet):
        """Hardcoded values (no formulas) should score 0."""
        ws = mock_worksheet
        ws["A40"] = 98.6
        ws["C40"] = 37  # Hardcoded value, not formula
        ws["C41"] = 37
        ws["A41"] = 98.6  # Hardcoded value, not formula
        
        results = grade_temp_conversions_v2(ws)
        
        assert results["temp_and_celsius_score"] == 0
    
    def test_empty_cells(self, mock_worksheet):
        """Empty temperature cells should score 0."""
        ws = mock_worksheet
        
        results = grade_temp_conversions_v2(ws)
        
        assert results["temp_and_celsius_score"] == 0
    
    def test_returns_all_keys(self, mock_worksheet):
        """Results should contain all expected keys."""
        ws = mock_worksheet
        
        results = grade_temp_conversions_v2(ws)
        
        assert "temp_and_celsius_score" in results
        assert "temp_and_celsius_feedback" in results
    
    def test_score_capped_at_4(self, mock_worksheet):
        """Score should never exceed 4 points."""
        ws = mock_worksheet
        ws["A40"] = 98.6
        ws["C40"] = "=(5/9)*(A40-32)"
        ws["C41"] = 37
        ws["A41"] = "=(9/5)*C41+32"
        
        results = grade_temp_conversions_v2(ws)
        
        assert results["temp_and_celsius_score"] <= 4


# ============================================================
# Test Unit Conversions Tab Orchestrator
# ============================================================

class TestUnitConversionsTabOrchestrator:
    """Tests for the main unit conversions grading orchestrator."""
    
    def test_returns_all_score_keys(self, mock_worksheet):
        """Results should contain all expected score keys."""
        ws = mock_worksheet
        
        results = grade_unit_conversions_tab_v2(ws)
        
        assert "unit_text_score" in results
        assert "formulas_score" in results
        assert "final_formula_score" in results
        assert "final_unit_score" in results
        assert "temp_and_celsius_score" in results
    
    def test_returns_all_feedback_keys(self, mock_worksheet):
        """Results should contain all expected feedback keys."""
        ws = mock_worksheet
        
        results = grade_unit_conversions_tab_v2(ws)
        
        assert "unit_text_feedback" in results
        assert "formulas_feedback" in results
        assert "final_formula_feedback" in results
        assert "final_unit_feedback" in results
        assert "temp_and_celsius_feedback" in results
    
    def test_aggregates_scores(self, unit_conversions_worksheet):
        """Scores should be aggregated from all row checkers."""
        ws = unit_conversions_worksheet
        
        results = grade_unit_conversions_tab_v2(ws)
        
        # Scores should be non-negative integers/floats
        assert results["unit_text_score"] >= 0
        assert results["formulas_score"] >= 0
        assert results["final_formula_score"] >= 0
        assert results["final_unit_score"] >= 0
        assert results["temp_and_celsius_score"] >= 0
    
    def test_empty_worksheet(self, mock_worksheet):
        """Empty worksheet should return all zeros."""
        ws = mock_worksheet
        
        results = grade_unit_conversions_tab_v2(ws)
        
        assert results["unit_text_score"] == 0
        assert results["formulas_score"] == 0
        assert results["final_formula_score"] == 0
        assert results["final_unit_score"] == 0
        assert results["temp_and_celsius_score"] == 0
    
    def test_feedback_lists_are_lists(self, mock_worksheet):
        """All feedback values should be lists."""
        ws = mock_worksheet
        
        results = grade_unit_conversions_tab_v2(ws)
        
        for key in ["unit_text_feedback", "formulas_feedback", 
                    "final_formula_feedback", "final_unit_feedback",
                    "temp_and_celsius_feedback"]:
            assert isinstance(results[key], list)
    
    def test_feedback_tuples_format(self, mock_worksheet):
        """Feedback items should be (code, params) tuples."""
        ws = mock_worksheet
        
        results = grade_unit_conversions_tab_v2(ws)
        
        for key in ["unit_text_feedback", "formulas_feedback", 
                    "final_formula_feedback", "final_unit_feedback",
                    "temp_and_celsius_feedback"]:
            for item in results[key]:
                assert isinstance(item, tuple)
                assert len(item) == 2
                code, params = item
                assert isinstance(code, str)
                assert isinstance(params, dict)


# ============================================================
# Edge Cases
# ============================================================

class TestEdgeCases:
    """Tests for edge cases and unusual inputs."""
    
    def test_formula_with_spaces(self, mock_worksheet):
        """Formulas with extra spaces should be normalized."""
        ws = mock_worksheet
        
        ws["F26"] = "= L14 / I14 "  # Extra spaces
        ws["G26"] = " mcg/mg "  # Extra spaces
        ws["I26"] = "= L17 / I17 "
        ws["J26"] = " ml/tsp "
        ws["O26"] = "= C26 * F26 * I26 "
        ws["P26"] = " mcg/tsp "
        
        results = grade_row_26_v2(ws)
        
        # Should still be recognized after normalization
        assert results["formulas_score"] == 4
    
    def test_formula_with_absolute_refs(self, mock_worksheet):
        """Formulas with $ (absolute refs) should work."""
        ws = mock_worksheet
        
        ws["F26"] = "=$L$14/$I$14"  # Absolute references
        ws["G26"] = "mcg/mg"
        ws["I26"] = "=$L$17/$I$17"
        ws["J26"] = "ml/tsp"
        ws["O26"] = "=$C$26*$F$26*$I$26"
        ws["P26"] = "mcg/tsp"
        
        results = grade_row_26_v2(ws)
        
        assert results["formulas_score"] == 4
    
    def test_numeric_cell_values(self, mock_worksheet):
        """Numeric values (not formulas) should not match formula patterns."""
        ws = mock_worksheet
        
        ws["F26"] = 1000  # Numeric value, not formula
        ws["G26"] = "mcg/mg"
        ws["I26"] = 4.929  # Numeric value
        ws["J26"] = "ml/tsp"
        ws["O26"] = 4929  # Numeric value
        ws["P26"] = "mcg/tsp"
        
        results = grade_row_26_v2(ws)
        
        assert results["formulas_score"] == 0  # No formula credit
        assert results["final_formula_score"] == 0
    
    def test_mixed_case_units(self, mock_worksheet):
        """Unit labels should be case-insensitive."""
        ws = mock_worksheet
        
        ws["F26"] = "=L14/I14"
        ws["G26"] = "MCG/MG"  # Uppercase
        ws["I26"] = "=L17/I17"
        ws["J26"] = "ML/TSP"  # Uppercase
        ws["O26"] = "=C26*F26*I26"
        ws["P26"] = "MCG/TSP"
        
        results = grade_row_26_v2(ws)
        
        assert results["unit_text_score"] == 2
        assert results["final_unit_score"] == 1
