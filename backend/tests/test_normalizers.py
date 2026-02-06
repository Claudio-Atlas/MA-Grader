"""
test_normalizers.py — Unit tests for utilities/normalizers.py

Tests all normalization functions used across grading modules to ensure
consistent behavior with various input formats and edge cases.
"""

import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.normalizers import (
    normalize_formula,
    normalize_unit_text,
    normalize_time_unit,
    normalize_temp_formula
)


class TestNormalizeFormula:
    """Tests for normalize_formula function."""
    
    def test_none_input(self):
        """None should return empty string."""
        assert normalize_formula(None) == ""
    
    def test_empty_string(self):
        """Empty string should return empty string."""
        assert normalize_formula("") == ""
    
    def test_whitespace_only(self):
        """Whitespace should be stripped."""
        assert normalize_formula("   ") == ""
    
    def test_removes_dollar_signs(self):
        """Absolute references ($) should be removed."""
        assert normalize_formula("=$A$1+$B$2") == "=A1+B2"
    
    def test_removes_spaces(self):
        """Spaces should be removed."""
        assert normalize_formula("= A1 + B2 ") == "=A1+B2"
    
    def test_uppercase_conversion(self):
        """Formulas should be converted to uppercase."""
        assert normalize_formula("=slope(a1:a10,b1:b10)") == "=SLOPE(A1:A10,B1:B10)"
    
    def test_removes_outer_parentheses(self):
        """Wrapping parentheses should be removed."""
        result = normalize_formula("(=A1+B2)")
        # After removing outer parens: =A1+B2
        assert "A1+B2" in result
    
    def test_complex_formula(self):
        """Complex formulas should be normalized correctly."""
        input_formula = "= $B$30 * $D$19 + $B$31 "
        expected = "=B30*D19+B31"
        assert normalize_formula(input_formula) == expected
    
    def test_preserves_operators(self):
        """Mathematical operators should be preserved."""
        assert normalize_formula("=A1*B1/C1+D1-E1") == "=A1*B1/C1+D1-E1"
    
    def test_preserves_function_calls(self):
        """Excel function names should be preserved (uppercase)."""
        assert normalize_formula("=SUM(a1:a10)") == "=SUM(A1:A10)"
        assert normalize_formula("=AVERAGE(b1:b10)") == "=AVERAGE(B1:B10)"


class TestNormalizeUnitText:
    """Tests for normalize_unit_text function."""
    
    def test_none_input(self):
        """None should return empty string."""
        assert normalize_unit_text(None) == ""
    
    def test_empty_string(self):
        """Empty string should return empty string."""
        assert normalize_unit_text("") == ""
    
    def test_lowercase_conversion(self):
        """Unit text should be converted to lowercase."""
        assert normalize_unit_text("MCG/MG") == "mcg/mg"
    
    def test_removes_spaces(self):
        """Spaces should be removed."""
        assert normalize_unit_text("mcg / mg") == "mcg/mg"
    
    def test_normalizes_hr_to_h(self):
        """'hr' should be normalized to 'h'."""
        assert normalize_unit_text("hr/d") == "h/d"
        # Note: "hours" is not normalized (only exact "hr" is replaced)
        assert normalize_unit_text("hours/day") == "hours/d"
    
    def test_normalizes_day_to_d(self):
        """'day' should be normalized to 'd'."""
        assert normalize_unit_text("h/day") == "h/d"
    
    def test_normalizes_year_to_yr(self):
        """'year' should be normalized to 'yr'."""
        assert normalize_unit_text("year/d") == "yr/d"
    
    def test_preserves_slashes(self):
        """Slashes in units should be preserved."""
        assert normalize_unit_text("mcg/tsp") == "mcg/tsp"
    
    def test_common_unit_formats(self):
        """Common unit formats should normalize correctly."""
        assert normalize_unit_text("ml/tsp") == "ml/tsp"
        assert normalize_unit_text("gal/l") == "gal/l"
        assert normalize_unit_text("kg/lb") == "kg/lb"


class TestNormalizeTimeUnit:
    """Tests for normalize_time_unit function."""
    
    def test_none_input(self):
        """None should return empty string."""
        assert normalize_time_unit(None) == ""
    
    def test_empty_string(self):
        """Empty string should return empty string."""
        assert normalize_time_unit("") == ""
    
    def test_normalizes_hr(self):
        """'hr' should be normalized to 'h'."""
        assert normalize_time_unit("hr") == "h"
        assert normalize_time_unit("hr/d") == "h/d"
    
    def test_normalizes_day(self):
        """'day' should be normalized to 'd'."""
        assert normalize_time_unit("day") == "d"
        assert normalize_time_unit("h/day") == "h/d"
    
    def test_normalizes_year(self):
        """'year' should be normalized to 'yr'."""
        assert normalize_time_unit("year") == "yr"
        assert normalize_time_unit("year/d") == "yr/d"
    
    def test_y_slash_to_yr_slash(self):
        """'y/' prefix should become 'yr/'."""
        assert normalize_time_unit("y/d") == "yr/d"


class TestNormalizeTempFormula:
    """Tests for normalize_temp_formula function."""
    
    def test_none_input(self):
        """None should return empty string."""
        assert normalize_temp_formula(None) == ""
    
    def test_empty_string(self):
        """Empty string should return empty string."""
        assert normalize_temp_formula("") == ""
    
    def test_removes_dollar_signs(self):
        """Absolute references should be removed."""
        assert normalize_temp_formula("=$A$40-32") == "=A40-32"
    
    def test_removes_spaces(self):
        """Spaces should be removed."""
        assert normalize_temp_formula("= (5/9) * (A40 - 32)") == "=(5/9)*(A40-32)"
    
    def test_uppercase_conversion(self):
        """Formula should be converted to uppercase."""
        assert normalize_temp_formula("=(5/9)*(a40-32)") == "=(5/9)*(A40-32)"
    
    def test_removes_outer_parentheses(self):
        """Outer wrapping parentheses should be removed."""
        result = normalize_temp_formula("((5/9)*(A40-32))")
        assert "5/9" in result and "A40-32" in result
    
    def test_preserves_inner_structure(self):
        """Inner formula structure should be preserved."""
        result = normalize_temp_formula("=(9/5)*C41+32")
        assert "9/5" in result
        assert "C41" in result
        assert "+32" in result


class TestEdgeCases:
    """Tests for edge cases across all normalizers."""
    
    def test_numeric_input_formula(self):
        """Numeric input should be converted to string."""
        assert normalize_formula(123) == "123"
    
    def test_numeric_input_unit(self):
        """Numeric input should be converted to string."""
        assert normalize_unit_text(123) == "123"
    
    def test_boolean_input_formula(self):
        """Boolean input should be converted to string."""
        assert normalize_formula(True) == "TRUE"
    
    def test_special_characters_preserved(self):
        """Special characters like : and , should be preserved."""
        assert normalize_formula("=SUM(A1:A10,B1:B10)") == "=SUM(A1:A10,B1:B10)"
    
    def test_mixed_case_cell_refs(self):
        """Mixed case cell references should be normalized."""
        assert normalize_formula("=a1+A2+aA3") == "=A1+A2+AA3"
