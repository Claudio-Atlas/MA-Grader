# graders/currency_conversion_v2/row20_budget_conversion_v2.py

import re
from ..currency_conversion.utils import norm_unit


def _formula_contains_refs(formula: str, required_refs: list) -> bool:
    """
    Check if a formula contains all required cell references.
    
    Args:
        formula: The formula string (e.g., '=B4*C19')
        required_refs: List of required cell refs (e.g., ['B4', 'C19'])
    
    Returns:
        True if ALL required references are found in the formula
    """
    if not formula:
        return False
    
    # Normalize: remove =, $, spaces, and lowercase
    cleaned = formula.lstrip("=").replace("$", "").replace(" ", "").lower()
    
    for ref in required_refs:
        ref_lower = ref.lower()
        if ref_lower not in cleaned:
            return False
    
    return True


def _get_cell_value_safe(sheet, cell_ref):
    """Safely get a cell's numeric value, returning None if not numeric."""
    try:
        val = sheet[cell_ref].value
        if val is None:
            return None
        return float(val)
    except (ValueError, TypeError):
        return None


def _values_match(actual, expected, tolerance=0.01):
    """Check if two values match within a relative tolerance (default 1%)."""
    if actual is None or expected is None:
        return False
    try:
        actual_f = float(actual)
        expected_f = float(expected)
        if expected_f == 0:
            return abs(actual_f) < 0.01
        return abs(actual_f - expected_f) / abs(expected_f) <= tolerance
    except (ValueError, TypeError):
        return False


def grade_row20_budget_conversion_v2(sheet, values_sheet=None):
    """
    Currency Conversion V2 - Row 20 (C20-F20)

    Rule (same as V1):
      - Each cell must multiply B4 by corresponding exchange rate cell:
          C20 = B4*C19 (or C19*B4)
          D20 = B4*D19 (or D19*B4)
          E20 = B4*E19 (or E19*B4)
          F20 = B4*F19 (or F19*B4)

    Scoring (UPDATED - bulletproof):
      - Formula correctness: 2.0 pts per cell (max 8.0)
        - Full credit if: formula contains B4 AND rate cell AND calculated value is correct
      - Formatting correctness: 0.25 pts per cell (max 1.0)
      - Total possible: 9.0

    Args:
        sheet: Worksheet with formulas (data_only=False)
        values_sheet: Worksheet with calculated values (data_only=True), optional

    Returns:
      (total_score, formula_score, format_score, feedback)
        feedback is list[(code, params)]
    """

    budget_cell = "B4"
    pairs = [("C20", "C19"), ("D20", "D19"), ("E20", "E19"), ("F20", "F19")]

    formula_score = 0.0
    format_score = 0.0
    feedback = []

    # Get B4 value for expected calculations
    b4_value = _get_cell_value_safe(sheet, budget_cell)

    for target_cell, rate_ref in pairs:
        raw_formula = sheet[target_cell].value

        # -----------------------------
        # Formula check (BULLETPROOF - refs + value)
        # -----------------------------
        if not isinstance(raw_formula, str) or not raw_formula.startswith("="):
            feedback.append(("CC20_FORMULA_MISSING", {"cell": target_cell, "rate_ref": rate_ref}))
        else:
            f = norm_unit(raw_formula)  # existing normalizer (lowercases & strips)

            # Method 1: Exact match (traditional)
            valid_1 = f == f"=b4*{rate_ref.lower()}"
            valid_2 = f == f"={rate_ref.lower()}*b4"
            exact_match = valid_1 or valid_2
            
            # Method 2: Check for required cell references (flexible)
            has_required_refs = _formula_contains_refs(raw_formula, [budget_cell, rate_ref])
            
            # Method 3: Verify calculated value is correct (if values_sheet provided)
            value_correct = False
            if values_sheet is not None and b4_value is not None:
                rate_value = _get_cell_value_safe(sheet, rate_ref)
                if rate_value is not None:
                    expected_value = b4_value * rate_value
                    actual_value = _get_cell_value_safe(values_sheet, target_cell)
                    value_correct = _values_match(actual_value, expected_value)

            # Award credit: need refs + value (if we can check), or exact match
            if exact_match:
                formula_score += 2.0
                feedback.append(("CC20_FORMULA_OK", {"cell": target_cell, "rate_ref": rate_ref}))
            elif has_required_refs:
                if values_sheet is None:
                    # Can't verify value, trust the references
                    formula_score += 2.0
                    feedback.append(("CC20_FORMULA_OK", {
                        "cell": target_cell, 
                        "rate_ref": rate_ref,
                        "note": "Formula uses correct cell references"
                    }))
                elif value_correct:
                    # References correct AND value correct - full credit
                    formula_score += 2.0
                    feedback.append(("CC20_FORMULA_OK", {
                        "cell": target_cell, 
                        "rate_ref": rate_ref,
                        "note": "Formula uses correct cell references and value is correct"
                    }))
                else:
                    # References correct but value wrong - no credit
                    feedback.append(("CC20_FORMULA_BAD", {
                        "cell": target_cell, 
                        "rate_ref": rate_ref,
                        "expected_a": f"=B4*{rate_ref}",
                        "expected_b": f"={rate_ref}*B4",
                        "note": "Formula has correct refs but calculated value is incorrect"
                    }))
            else:
                feedback.append((
                    "CC20_FORMULA_BAD",
                    {"cell": target_cell, "rate_ref": rate_ref, "expected_a": f"=B4*{rate_ref}", "expected_b": f"={rate_ref}*B4"}
                ))

        # -----------------------------
        # Formatting: Currency with 2 decimals
        # (same acceptance logic as V1)
        # -----------------------------
        num_fmt = str(sheet[target_cell].number_format).lower()
        if "$" in num_fmt or "currency" in num_fmt or "0.00" in num_fmt:
            format_score += 0.25
            feedback.append(("CC20_FORMAT_OK", {"cell": target_cell}))
        else:
            feedback.append(("CC20_FORMAT_BAD", {"cell": target_cell}))

    total_score = round(formula_score + format_score, 2)

    feedback.insert(0, (
        "CC20_SUMMARY",
        {
            "formula": round(formula_score, 2),
            "formula_possible": 8.0,
            "formatting": round(format_score, 2),
            "formatting_possible": 1.0,
            "total": total_score,
            "total_possible": 9.0
        }
    ))

    return total_score, round(formula_score, 2), round(format_score, 2), feedback
