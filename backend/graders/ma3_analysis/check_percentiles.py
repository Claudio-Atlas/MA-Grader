"""
check_percentiles.py — Validates percentile calculations in G27:G28

Grading: 6 points total (3 pts each)

Expected formula patterns:
    PERCENTILE(range, value)
    PERCENTILE.INC(range, value)
    PERCENTILE.EXC(range, value)
    
G27 should be the 25th percentile (value ~0.25)
G28 should be the 75th percentile (value ~0.75)
"""

import re
from typing import Tuple, List, Optional
from openpyxl.worksheet.worksheet import Worksheet


def _normalize_formula(formula: str) -> str:
    """Normalize formula for comparison."""
    if not formula:
        return ""
    return formula.replace(" ", "").upper()


def _extract_percentile_value(formula: str) -> Optional[float]:
    """
    Extract the percentile value from a PERCENTILE formula.
    
    Returns the decimal value (e.g., 0.25, 0.75) or None if not found.
    """
    if not formula:
        return None
    
    normalized = _normalize_formula(formula)
    
    # Pattern to find percentile value: ,0.XX) or ,0.X)
    # Matches: PERCENTILE(range,0.25), PERCENTILE.INC(range,0.75), etc.
    match = re.search(r',\s*(0\.\d+)\s*\)', normalized)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    
    return None


def _check_percentile_formula(formula: str, cell_ref: str) -> Tuple[bool, str]:
    """
    Check if formula uses a PERCENTILE function with correct range AND value.
    
    G27 should be ~25th percentile (0.25 ± 0.05)
    G28 should be ~75th percentile (0.75 ± 0.05)
    
    Returns: (is_correct, reason)
    """
    if not formula or not formula.startswith("="):
        return False, "Not a formula"
    
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
        return False, "Missing PERCENTILE function"
    
    # Check for correct range reference (D14:D63 or ANCHORARRAY variant)
    range_patterns = ["D14:D63", "$D$14:$D$63", "$D14:$D63", "ANCHORARRAY"]
    has_correct_range = any(pattern in normalized for pattern in range_patterns)
    
    if not has_correct_range:
        return False, "Incorrect range reference"
    
    # Extract and validate the percentile value
    pct_value = _extract_percentile_value(formula)
    
    if pct_value is None:
        # Could not extract value - might be a cell reference, give partial credit
        return True, "Could not verify percentile value"
    
    # Validate percentile value based on cell
    if cell_ref == "G27":
        # Should be 25th percentile (0.25 ± tolerance)
        if 0.20 <= pct_value <= 0.30:
            return True, "Correct"
        else:
            return False, f"Expected ~0.25 for 25th percentile, found {pct_value}"
    elif cell_ref == "G28":
        # Should be 75th percentile (0.75 ± tolerance)
        if 0.70 <= pct_value <= 0.80:
            return True, "Correct"
        else:
            return False, f"Expected ~0.75 for 75th percentile, found {pct_value}"
    
    return True, "OK"


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
        else:
            is_correct, reason = _check_percentile_formula(formula, cell_ref)
            if is_correct:
                correct_count += 1
                feedback.append(("PERCENTILE_OK", {"cell": cell_ref}))
            else:
                feedback.append(("PERCENTILE_WRONG", {
                    "cell": cell_ref,
                    "reason": reason,
                    "found": formula
                }))
    
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
