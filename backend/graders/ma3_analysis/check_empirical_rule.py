"""
check_empirical_rule.py — Validates empirical rule calculations in G36:G37

Grading: 6 points total (3 pts each)

Expected formulas:
    G36 (Lower Bound): =I18-I20  (Mean - StdDev)
    G37 (Upper Bound): =I18+I20  (Mean + StdDev)
"""

import re
from typing import Tuple, List
from openpyxl.worksheet.worksheet import Worksheet


def _normalize_formula(formula: str) -> str:
    """Normalize formula for comparison."""
    if not formula:
        return ""
    return formula.replace(" ", "").upper()


def _check_lower_bound_formula(formula: str) -> bool:
    """
    Check if formula calculates Mean - StdDev.
    Expected: =I18-I20 or equivalent
    """
    if not formula or not formula.startswith("="):
        return False
    
    normalized = _normalize_formula(formula)
    
    # Must have I18 (mean) and I20 (stdev) with subtraction
    # Accept various patterns
    valid_patterns = [
        "=I18-I20",
        "=$I$18-$I$20",
        "=$I$18-I20",
        "=I18-$I$20",
        "=(I18-I20)",
        "=($I$18-$I$20)",
    ]
    
    normalized_patterns = [_normalize_formula(p) for p in valid_patterns]
    
    if normalized in normalized_patterns:
        return True
    
    # Also check for AVERAGE - STDEV pattern (if they recalculate)
    if "I18" in normalized and "I20" in normalized and "-" in normalized:
        return True
    
    return False


def _check_upper_bound_formula(formula: str) -> bool:
    """
    Check if formula calculates Mean + StdDev.
    Expected: =I18+I20 or equivalent
    """
    if not formula or not formula.startswith("="):
        return False
    
    normalized = _normalize_formula(formula)
    
    # Must have I18 (mean) and I20 (stdev) with addition
    valid_patterns = [
        "=I18+I20",
        "=$I$18+$I$20",
        "=$I$18+I20",
        "=I18+$I$20",
        "=(I18+I20)",
        "=($I$18+$I$20)",
    ]
    
    normalized_patterns = [_normalize_formula(p) for p in valid_patterns]
    
    if normalized in normalized_patterns:
        return True
    
    # Also check for presence of both cells with addition
    if "I18" in normalized and "I20" in normalized and "+" in normalized:
        return True
    
    return False


def check_empirical_rule(sheet: Worksheet) -> Tuple[float, List[Tuple[str, dict]]]:
    """
    Check empirical rule formulas in G36 (lower) and G37 (upper).
    
    Args:
        sheet: Analysis worksheet
        
    Returns:
        Tuple of (score, feedback_list)
    """
    feedback = []
    correct_count = 0
    points_per_cell = 3.0
    
    # Check Lower Bound (G36)
    cell_ref = "G36"
    cell = sheet[cell_ref]
    formula = cell.value
    
    if formula is None or str(formula).strip() == "":
        feedback.append(("EMPIRICAL_LOWER_MISSING", {"cell": cell_ref}))
    elif not isinstance(formula, str) or not formula.startswith("="):
        feedback.append(("EMPIRICAL_LOWER_WRONG", {"cell": cell_ref}))
    elif _check_lower_bound_formula(formula):
        correct_count += 1
        feedback.append(("EMPIRICAL_LOWER_OK", {"cell": cell_ref}))
    else:
        feedback.append(("EMPIRICAL_LOWER_WRONG", {"cell": cell_ref}))
    
    # Check Upper Bound (G37)
    cell_ref = "G37"
    cell = sheet[cell_ref]
    formula = cell.value
    
    if formula is None or str(formula).strip() == "":
        feedback.append(("EMPIRICAL_UPPER_MISSING", {"cell": cell_ref}))
    elif not isinstance(formula, str) or not formula.startswith("="):
        feedback.append(("EMPIRICAL_UPPER_WRONG", {"cell": cell_ref}))
    elif _check_upper_bound_formula(formula):
        correct_count += 1
        feedback.append(("EMPIRICAL_UPPER_OK", {"cell": cell_ref}))
    else:
        feedback.append(("EMPIRICAL_UPPER_WRONG", {"cell": cell_ref}))
    
    # Calculate score
    score = round(correct_count * points_per_cell, 2)
    
    # Summary feedback
    if correct_count == 2:
        feedback = [("EMPIRICAL_ALL_CORRECT", {})]
    elif correct_count == 0:
        feedback.insert(0, ("EMPIRICAL_NONE_CORRECT", {}))
    else:
        feedback.insert(0, ("EMPIRICAL_PARTIAL", {"correct": correct_count}))
    
    return score, feedback
