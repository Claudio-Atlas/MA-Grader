# graders/unit_conversions/temp_conversions_v2.py

from graders.unit_conversions.utils import norm_formula


def _get_cell_value(sheet, cell_ref: str):
    """Get the numeric value of a cell (handles both values and cached formula results)."""
    try:
        cell = sheet[cell_ref]
        value = cell.value
        
        # If it's a formula, we can't evaluate it directly
        # But we can check if there's a cached value
        if isinstance(value, str) and value.startswith("="):
            return None
            
        if value is None:
            return None
            
        return float(value)
    except (TypeError, ValueError):
        return None


def _check_c40_calculated_value(sheet) -> bool:
    """
    Check if C40 has the correct calculated value for Fahrenheit to Celsius.
    Formula: (5/9) * (A40 - 32)
    """
    try:
        a40_val = _get_cell_value(sheet, "A40")
        c40_val = _get_cell_value(sheet, "C40")
        
        if a40_val is None or c40_val is None:
            return False
            
        expected = (5/9) * (a40_val - 32)
        return abs(expected - c40_val) < 0.01
    except (TypeError, ValueError):
        return False


def _check_a41_calculated_value(sheet) -> bool:
    """
    Check if A41 has the correct calculated value for Celsius to Fahrenheit.
    Formula: (9/5) * C41 + 32
    """
    try:
        c41_val = _get_cell_value(sheet, "C41")
        a41_val = _get_cell_value(sheet, "A41")
        
        if c41_val is None or a41_val is None:
            return False
            
        expected = (9/5) * c41_val + 32
        return abs(expected - a41_val) < 0.01
    except (TypeError, ValueError):
        return False


def grade_temp_conversions_v2(sheet):
    """
    V2 JSON-driven strict grader for temperature conversions on the Unit Conversions tab.
    
    Checks:
      * C40 = (5/9)*(A40-32)
      * A41 = (9/5)*C41 + 32
    Accepts parentheses, spacing differences, and reordered but equivalent expressions.
    
    Scoring:
      * Full credit (2 pts): Has formula with correct cell refs
      * Partial credit (1 pt): Has formula with correct calculated value but no cell refs
      * No credit (0 pts): No formula or wrong value
    """

    # ----------------------- Score buckets -----------------------
    score = 0        # 4 points max (2 for each formula)
    feedback = []    # list of (code, params)

    # ----------------------- Extract and normalize -----------------------
    c40 = norm_formula(sheet["C40"].value)
    a41 = norm_formula(sheet["A41"].value)

    # C40 requirements (cell refs)
    required_c40 = {
        "A40-32",
        "5/9"
    }

    # A41 requirements (cell refs)
    required_a41 = {
        "C41",
        "9/5",
        "+32"
    }

    # ============================================================
    # 1. Grade C40 formula
    # ============================================================

    c40_has_formula = isinstance(c40, str) and c40.startswith("=") and "*" in c40
    c40_has_refs = c40_has_formula and all(fragment in c40 for fragment in required_c40)

    if c40_has_refs:
        # Full credit: formula with cell references
        score += 2
        feedback.append(("UC_TEMP_C40_CORRECT", {"cell": "C40"}))
    elif c40_has_formula and _check_c40_calculated_value(sheet):
        # Partial credit: formula without cell refs but correct value
        score += 1
        feedback.append(("UC_TEMP_C40_PARTIAL", {
            "cell": "C40",
            "note": "Formula produces correct value but missing cell reference (A40). Use cell references for full credit."
        }))
    else:
        feedback.append(("UC_TEMP_C40_INCORRECT",
                         {"cell": "C40", "required": list(required_c40)}))

    # ============================================================
    # 2. Grade A41 formula
    # ============================================================

    a41_has_formula = isinstance(a41, str) and a41.startswith("=") and "*" in a41
    a41_has_refs = a41_has_formula and all(fragment in a41 for fragment in required_a41)

    if a41_has_refs:
        # Full credit: formula with cell references
        score += 2
        feedback.append(("UC_TEMP_A41_CORRECT", {"cell": "A41"}))
    elif a41_has_formula and _check_a41_calculated_value(sheet):
        # Partial credit: formula without cell refs but correct value
        score += 1
        feedback.append(("UC_TEMP_A41_PARTIAL", {
            "cell": "A41", 
            "note": "Formula produces correct value but missing cell reference (C41). Use cell references for full credit."
        }))
    else:
        feedback.append(("UC_TEMP_A41_INCORRECT",
                         {"cell": "A41", "required": list(required_a41)}))

    # ============================================================
    # 3. Clamp and return V2 structured output
    # ============================================================

    return {
        "temp_and_celsius_score": min(score, 4),
        "temp_and_celsius_feedback": feedback
    }
