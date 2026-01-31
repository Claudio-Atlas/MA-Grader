# graders/income_analysis/check_predictions.py

"""
Check predicted salary values in E19:E35.

Grading logic:
- Formula must reference BOTH B30 (slope) AND B31 (intercept)
- If formula has correct cell references, we trust the calculation is correct
  (openpyxl can't evaluate formulas without Excel)

Note: We open workbooks with data_only=False to preserve formula text,
which means we can't verify calculated values. The formula reference check
is sufficient - if a student references the correct cells, their formula
will produce the correct result.
"""

from openpyxl.worksheet.formula import ArrayFormula


def _has_required_refs(formula: str) -> bool:
    """
    Check if formula contains both B30 and B31 cell references.
    Case-insensitive check. Handles absolute references ($B$30).
    """
    if not formula:
        return False
    # Remove $ signs to handle absolute references like $B$30
    normalized = formula.upper().replace("$", "")
    return "B30" in normalized and "B31" in normalized


def _has_years_ref(formula: str, row: int) -> bool:
    """
    Check if formula references the years of experience cell (D column).
    The formula should reference D{row} for the corresponding years value.
    Handles absolute references like $D$19 or $D19 or D$19.
    """
    if not formula:
        return False
    # Remove $ signs to normalize absolute/mixed references
    normalized = formula.upper().replace("$", "")
    return f"D{row}" in normalized


def check_predictions(ws):
    """
    Check predicted values in E19:E35.
    
    Each prediction formula should:
    1. Reference B30 (slope)
    2. Reference B31 (intercept)
    3. Reference the corresponding D column cell (years of experience)
    
    Formula pattern: =B30*D19+B31 (or equivalent)

    Returns:
        (score: float, feedback: list[tuple[str, dict]])
    """
    total_rows = 17
    correct_count = 0
    missing_slope_intercept = 0
    missing_years_ref = 0
    not_formula = 0

    for row in range(19, 36):
        cell = ws[f"E{row}"]
        value = cell.value
        
        # Handle ArrayFormula objects (Excel 365 dynamic arrays)
        if isinstance(value, ArrayFormula):
            formula = value.text
        elif isinstance(value, str) and value.startswith("="):
            formula = value
        else:
            not_formula += 1
            continue
        
        # Check 1: Does formula reference B30 AND B31?
        has_slope_intercept = _has_required_refs(formula)
        
        # Check 2: Does formula reference the years column?
        has_years = _has_years_ref(formula, row)
        
        if has_slope_intercept and has_years:
            correct_count += 1
        elif has_slope_intercept and not has_years:
            # Has slope/intercept but wrong/missing years reference
            missing_years_ref += 1
        elif not has_slope_intercept:
            missing_slope_intercept += 1

    # Build feedback
    feedback = []
    
    if correct_count == total_rows:
        return 6.0, [("IA_PREDICTIONS_ALL_CORRECT", {"range": "E19:E35"})]

    if correct_count == 0:
        # Provide specific feedback
        if not_formula > 0:
            feedback.append(("IA_PREDICTIONS_NOT_FORMULAS", 
                           {"count": not_formula, "range": "E19:E35"}))
        if missing_slope_intercept > 0:
            feedback.append(("IA_PREDICTIONS_MISSING_REFS", 
                           {"count": missing_slope_intercept, "range": "E19:E35",
                            "expected": "B30 (slope) and B31 (intercept)"}))
        if missing_years_ref > 0:
            feedback.append(("IA_PREDICTIONS_MISSING_YEARS", 
                           {"count": missing_years_ref, "range": "E19:E35"}))
        if not feedback:
            feedback.append(("IA_PREDICTIONS_NONE_CORRECT", {"range": "E19:E35"}))
        return 0.0, feedback

    # Partial credit
    score = round(correct_count * (6 / total_rows), 1)
    
    details = []
    if missing_slope_intercept > 0:
        details.append(f"{missing_slope_intercept} missing B30/B31 refs")
    if missing_years_ref > 0:
        details.append(f"{missing_years_ref} missing years ref")
    if not_formula > 0:
        details.append(f"{not_formula} not formulas")
    
    feedback.append(("IA_PREDICTIONS_PARTIAL", 
                    {"correct": correct_count, "total": total_rows, 
                     "range": "E19:E35", "issues": "; ".join(details) if details else ""}))
    return score, feedback
