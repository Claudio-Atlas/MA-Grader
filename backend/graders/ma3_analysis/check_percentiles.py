"""
check_percentiles.py — Validates percentile calculations in G27:G28

Grading: 6 points total (3 pts each)

Expected formula patterns:
    PERCENTILE(range, value)
    PERCENTILE.INC(range, value)
    PERCENTILE.EXC(range, value)
    
The percentile values are dynamically determined by the student's name,
so we just verify the function is used correctly with the D14:D63 range.
"""

import re
from typing import Tuple, List
from openpyxl.worksheet.worksheet import Worksheet


def _normalize_formula(formula: str) -> str:
    """Normalize formula for comparison."""
    if not formula:
        return ""
    return formula.replace(" ", "").upper()


def _check_percentile_formula(formula: str) -> bool:
    """
    Check if formula uses a PERCENTILE function with correct range.
    
    Valid functions: PERCENTILE, PERCENTILE.INC, PERCENTILE.EXC
    Must reference D14:D63 range
    """
    if not formula or not formula.startswith("="):
        return False
    
    normalized = _normalize_formula(formula)
    
    # Check for PERCENTILE function (with or without _xlfn. prefix)
    has_percentile = any(p in normalized for p in [
        "PERCENTILE(",
        "PERCENTILE.INC(",
        "PERCENTILE.EXC(",
        "_XLFN.PERCENTILE.INC(",
        "_XLFN.PERCENTILE.EXC(",
    ])
    
    if not has_percentile:
        return False
    
    # Check for correct range reference (D14:D63)
    range_patterns = ["D14:D63", "$D$14:$D$63", "$D14:$D63"]
    has_correct_range = any(pattern in normalized for pattern in range_patterns)
    
    return has_correct_range


def check_percentiles(sheet: Worksheet) -> Tuple[float, List[Tuple[str, dict]]]:
    """
    Check percentile formulas in G27 and G28.
    
    Args:
        sheet: Analysis worksheet
        
    Returns:
        Tuple of (score, feedback_list)
    """
    feedback = []
    correct_count = 0
    total_cells = 2
    points_per_cell = 3.0
    
    cells_to_check = ["G27", "G28"]
    
    for cell_ref in cells_to_check:
        cell = sheet[cell_ref]
        formula = cell.value
        
        if formula is None or str(formula).strip() == "":
            feedback.append(("PERCENTILE_MISSING", {"cell": cell_ref}))
        elif not isinstance(formula, str) or not formula.startswith("="):
            feedback.append(("PERCENTILE_WRONG", {"cell": cell_ref}))
        elif _check_percentile_formula(formula):
            correct_count += 1
            feedback.append(("PERCENTILE_OK", {"cell": cell_ref}))
        else:
            feedback.append(("PERCENTILE_WRONG", {"cell": cell_ref}))
    
    # Calculate score
    score = round(correct_count * points_per_cell, 2)
    
    # Summary feedback
    if correct_count == total_cells:
        feedback = [("PERCENTILE_ALL_CORRECT", {})]
    elif correct_count == 0:
        feedback.insert(0, ("PERCENTILE_NONE_CORRECT", {}))
    else:
        feedback.insert(0, ("PERCENTILE_PARTIAL", {"correct": correct_count}))
    
    return score, feedback
