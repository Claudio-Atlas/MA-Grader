# graders/income_analysis/check_predictions.py

from typing import Optional


def _has_required_refs(formula: str) -> bool:
    """
    Check if formula contains both B30 and B31 cell references (case-insensitive).
    """
    if not formula:
        return False
    upper = formula.upper()
    return "B30" in upper and "B31" in upper


def _calculate_expected_value(ws, row: int) -> Optional[float]:
    """
    Calculate the expected prediction value using slope (B30) and intercept (B31).
    Expected formula: slope * years_experience + intercept
    """
    try:
        slope = ws["B30"].value
        intercept = ws["B31"].value
        years = ws[f"D{row}"].value
        
        # Handle formulas - get calculated value if it's a formula
        if isinstance(slope, str) and slope.startswith("="):
            # Can't evaluate formula directly, skip calculation check
            return None
        if isinstance(intercept, str) and intercept.startswith("="):
            return None
        if isinstance(years, str) and years.startswith("="):
            return None
            
        if slope is None or intercept is None or years is None:
            return None
            
        return float(slope) * float(years) + float(intercept)
    except (TypeError, ValueError):
        return None


def _get_cell_calculated_value(ws, cell_ref: str) -> Optional[float]:
    """
    Get the calculated/displayed value of a cell.
    For openpyxl, this requires data_only=True mode or cached values.
    """
    try:
        cell = ws[cell_ref]
        value = cell.value
        
        # If it's a formula, try to get cached value
        if isinstance(value, str) and value.startswith("="):
            # openpyxl doesn't evaluate formulas, but Excel caches results
            # Try the cached value if available
            if hasattr(cell, 'cached_value') and cell.cached_value is not None:
                return float(cell.cached_value)
            return None
        
        if value is None:
            return None
            
        return float(value)
    except (TypeError, ValueError):
        return None


def check_predictions(ws):
    """
    Check predicted values in E19-E35.
    
    Grading logic:
    1. Formula must contain B30 AND B31 (cell references to slope/intercept)
    2. Calculated value must be correct (within tolerance)
    3. Both conditions must pass for full credit on each row

    Returns:
        (score: float, feedback: list[tuple[str, dict]])
    """
    total_rows = 17
    correct_count = 0
    has_refs_no_value = 0
    has_value_no_refs = 0

    for row in range(19, 36):
        cell = ws[f"E{row}"]
        formula = cell.value
        
        # Check 1: Does formula contain B30 and B31?
        has_refs = False
        if isinstance(formula, str) and formula.startswith("="):
            has_refs = _has_required_refs(formula)
        
        # Check 2: Is the calculated value correct?
        # Get expected value from slope * years + intercept
        expected = _calculate_expected_value(ws, row)
        actual = _get_cell_calculated_value(ws, f"E{row}")
        
        value_correct = False
        if expected is not None and actual is not None:
            # Allow small tolerance for floating point
            value_correct = abs(expected - actual) < 0.01
        
        # Both must pass for full credit
        if has_refs and value_correct:
            correct_count += 1
        elif has_refs and not value_correct:
            has_refs_no_value += 1
        elif not has_refs and value_correct:
            has_value_no_refs += 1

    # Build feedback
    feedback = []
    
    if correct_count == total_rows:
        return 6.0, [("IA_PREDICTIONS_ALL_CORRECT", {"range": "E19:E35"})]

    if correct_count == 0:
        # Provide more specific feedback
        if has_refs_no_value > 0:
            feedback.append(("IA_PREDICTIONS_REFS_BUT_WRONG_VALUE", 
                           {"count": has_refs_no_value, "range": "E19:E35"}))
        if has_value_no_refs > 0:
            feedback.append(("IA_PREDICTIONS_VALUE_BUT_NO_REFS", 
                           {"count": has_value_no_refs, "range": "E19:E35"}))
        if not feedback:
            feedback.append(("IA_PREDICTIONS_NONE_CORRECT", {"range": "E19:E35"}))
        return 0.0, feedback

    score = round(correct_count * (6 / total_rows), 1)
    feedback.append(("IA_PREDICTIONS_PARTIAL", 
                    {"correct": correct_count, "total": total_rows, "range": "E19:E35"}))
    return score, feedback
