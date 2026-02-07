"""
check_differences.py — Validates difference calculations in D14:D63

Grading: 6 points total (0.12 pts each for 50 cells)
Expected formula pattern: =C{row}-B{row}
"""

import re
from typing import Tuple, List
from openpyxl.worksheet.worksheet import Worksheet


def _normalize_formula(formula: str) -> str:
    """Normalize formula for comparison (remove spaces, uppercase)."""
    if not formula:
        return ""
    return formula.replace(" ", "").upper()


def _is_valid_difference_formula(formula: str, row: int) -> bool:
    """
    Check if formula correctly calculates After - Before for this row.
    
    Valid patterns:
        =C14-B14
        =C14 - B14
        =$C$14-$B$14
        =SUM(C14-B14)  (equivalent result)
        =(C14-B14)
    """
    if not formula or not formula.startswith("="):
        return False
    
    normalized = _normalize_formula(formula)
    
    # Pattern: =C{row}-B{row} with optional $ signs
    patterns = [
        f"=C{row}-B{row}",
        f"=$C${row}-$B${row}",
        f"=$C{row}-$B{row}",
        f"=C${row}-B${row}",
        f"=$C${row}-B{row}",
        f"=C{row}-$B${row}",
        # Wrapped in parentheses
        f"=(C{row}-B{row})",
        f"=($C${row}-$B${row})",
        # Wrapped in SUM (same result)
        f"=SUM(C{row}-B{row})",
        f"=SUM($C${row}-$B${row})",
    ]
    
    normalized_patterns = [_normalize_formula(p) for p in patterns]
    
    return normalized in normalized_patterns


def check_differences(sheet: Worksheet) -> Tuple[float, List[Tuple[str, dict]]]:
    """
    Check difference formulas in D14:D63.
    
    Args:
        sheet: Analysis worksheet
        
    Returns:
        Tuple of (score, feedback_list)
    """
    feedback = []
    correct_count = 0
    total_cells = 50
    points_per_cell = 6.0 / total_cells  # 0.12 per cell
    
    for row in range(14, 64):  # Rows 14-63
        cell = sheet[f"D{row}"]
        cell_ref = f"D{row}"
        
        # Get the formula (not the calculated value)
        formula = cell.value
        
        # Check if it's a formula
        if formula is None:
            feedback.append(("DIFF_FORMULA_MISSING", {"cell": cell_ref, "row": row}))
        elif not isinstance(formula, str) or not formula.startswith("="):
            feedback.append(("DIFF_NOT_FORMULA", {"cell": cell_ref}))
        elif _is_valid_difference_formula(formula, row):
            correct_count += 1
            # Only add individual OK feedback if there are errors (to avoid 50 OK messages)
        else:
            feedback.append(("DIFF_FORMULA_WRONG", {
                "cell": cell_ref, 
                "row": row,
                "found": formula
            }))
    
    # Calculate score
    score = round(correct_count * points_per_cell, 2)
    
    # Summary feedback
    if correct_count == total_cells:
        feedback = [("DIFF_ALL_CORRECT", {})]
    elif correct_count == 0:
        feedback.insert(0, ("DIFF_NONE_CORRECT", {}))
    else:
        feedback.insert(0, ("DIFF_PARTIAL", {"correct": correct_count}))
    
    return score, feedback
