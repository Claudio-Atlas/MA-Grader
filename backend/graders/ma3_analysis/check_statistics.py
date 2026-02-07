"""
check_statistics.py — Validates statistics formulas (Mean, Median, StdDev, Range)

Grading: 24 points total (2 pts each × 12 cells)

Cell layout:
         G (Before)    H (After)    I (Difference)
Row 18:  Mean          Mean         Mean
Row 19:  Median        Median       Median  
Row 20:  StdDev        StdDev       StdDev
Row 21:  Range         Range        Range
"""

import re
from typing import Tuple, List
from openpyxl.worksheet.worksheet import Worksheet


def _normalize_formula(formula: str) -> str:
    """Normalize formula for comparison."""
    if not formula:
        return ""
    return formula.replace(" ", "").upper()


def _extract_function_name(formula: str) -> str:
    """Extract the main function name from a formula."""
    if not formula or not formula.startswith("="):
        return ""
    
    normalized = _normalize_formula(formula)
    
    # Match function name at start (after =)
    match = re.match(r'^=([A-Z_.]+)\(', normalized)
    if match:
        return match.group(1)
    
    # Check for _xlfn. prefix (Excel internal format)
    match = re.match(r'^=_XLFN\.([A-Z_.]+)\(', normalized)
    if match:
        return match.group(1)
    
    return ""


def _check_mean_formula(formula: str, col: str) -> bool:
    """Check if formula uses AVERAGE function with correct range."""
    func = _extract_function_name(formula)
    if func != "AVERAGE":
        return False
    
    normalized = _normalize_formula(formula)
    
    # Should reference the correct column (B, C, or D) rows 14-63
    col_map = {"G": "B", "H": "C", "I": "D"}
    expected_col = col_map.get(col, "")
    
    # Check for the data range pattern
    range_patterns = [
        f"{expected_col}14:{expected_col}63",
        f"${expected_col}$14:${expected_col}$63",
        f"${expected_col}14:${expected_col}63",
    ]
    
    for pattern in range_patterns:
        if pattern in normalized:
            return True
    
    return False


def _check_median_formula(formula: str, col: str) -> bool:
    """Check if formula uses MEDIAN function with correct range."""
    func = _extract_function_name(formula)
    if func != "MEDIAN":
        return False
    
    normalized = _normalize_formula(formula)
    col_map = {"G": "B", "H": "C", "I": "D"}
    expected_col = col_map.get(col, "")
    
    range_patterns = [
        f"{expected_col}14:{expected_col}63",
        f"${expected_col}$14:${expected_col}$63",
    ]
    
    for pattern in range_patterns:
        if pattern in normalized:
            return True
    
    return False


def _check_stdev_formula(formula: str, col: str) -> bool:
    """Check if formula uses STDEV, STDEV.P, or STDEV.S function."""
    func = _extract_function_name(formula)
    
    # Accept any STDEV variant
    valid_funcs = ["STDEV", "STDEV.P", "STDEV.S"]
    if func not in valid_funcs:
        return False
    
    normalized = _normalize_formula(formula)
    col_map = {"G": "B", "H": "C", "I": "D"}
    expected_col = col_map.get(col, "")
    
    range_patterns = [
        f"{expected_col}14:{expected_col}63",
        f"${expected_col}$14:${expected_col}$63",
    ]
    
    for pattern in range_patterns:
        if pattern in normalized:
            return True
    
    return False


def _check_range_formula(formula: str, col: str) -> bool:
    """Check if formula calculates MAX - MIN."""
    if not formula or not formula.startswith("="):
        return False
    
    normalized = _normalize_formula(formula)
    col_map = {"G": "B", "H": "C", "I": "D"}
    expected_col = col_map.get(col, "")
    
    # Must contain both MAX and MIN
    if "MAX(" not in normalized or "MIN(" not in normalized:
        return False
    
    # Must reference correct column
    if expected_col not in normalized:
        return False
    
    # Should have subtraction
    if "-" not in normalized:
        return False
    
    return True


def check_statistics(sheet: Worksheet) -> Tuple[float, List[Tuple[str, dict]]]:
    """
    Check statistics formulas in G18:I21.
    
    Args:
        sheet: Analysis worksheet
        
    Returns:
        Tuple of (score, feedback_list)
    """
    feedback = []
    correct_count = 0
    total_cells = 12
    points_per_cell = 2.0
    
    # Define the checks
    checks = [
        # (row, col, stat_type, check_func, ok_code, wrong_code, missing_code)
        (18, "G", "Mean", _check_mean_formula, "STAT_MEAN_OK", "STAT_MEAN_WRONG", "STAT_MEAN_MISSING"),
        (18, "H", "Mean", _check_mean_formula, "STAT_MEAN_OK", "STAT_MEAN_WRONG", "STAT_MEAN_MISSING"),
        (18, "I", "Mean", _check_mean_formula, "STAT_MEAN_OK", "STAT_MEAN_WRONG", "STAT_MEAN_MISSING"),
        (19, "G", "Median", _check_median_formula, "STAT_MEDIAN_OK", "STAT_MEDIAN_WRONG", "STAT_MEDIAN_MISSING"),
        (19, "H", "Median", _check_median_formula, "STAT_MEDIAN_OK", "STAT_MEDIAN_WRONG", "STAT_MEDIAN_MISSING"),
        (19, "I", "Median", _check_median_formula, "STAT_MEDIAN_OK", "STAT_MEDIAN_WRONG", "STAT_MEDIAN_MISSING"),
        (20, "G", "StdDev", _check_stdev_formula, "STAT_STDEV_OK", "STAT_STDEV_WRONG", "STAT_STDEV_MISSING"),
        (20, "H", "StdDev", _check_stdev_formula, "STAT_STDEV_OK", "STAT_STDEV_WRONG", "STAT_STDEV_MISSING"),
        (20, "I", "StdDev", _check_stdev_formula, "STAT_STDEV_OK", "STAT_STDEV_WRONG", "STAT_STDEV_MISSING"),
        (21, "G", "Range", _check_range_formula, "STAT_RANGE_OK", "STAT_RANGE_WRONG", "STAT_RANGE_MISSING"),
        (21, "H", "Range", _check_range_formula, "STAT_RANGE_OK", "STAT_RANGE_WRONG", "STAT_RANGE_MISSING"),
        (21, "I", "Range", _check_range_formula, "STAT_RANGE_OK", "STAT_RANGE_WRONG", "STAT_RANGE_MISSING"),
    ]
    
    for row, col, stat_type, check_func, ok_code, wrong_code, missing_code in checks:
        cell_ref = f"{col}{row}"
        cell = sheet[cell_ref]
        formula = cell.value
        
        if formula is None or str(formula).strip() == "":
            feedback.append((missing_code, {"cell": cell_ref}))
        elif not isinstance(formula, str) or not formula.startswith("="):
            feedback.append((wrong_code, {"cell": cell_ref}))
        elif check_func(formula, col):
            correct_count += 1
        else:
            feedback.append((wrong_code, {"cell": cell_ref}))
    
    # Calculate score
    score = round(correct_count * points_per_cell, 2)
    
    # Summary feedback
    if correct_count == total_cells:
        feedback = [("STATS_ALL_CORRECT", {})]
    elif correct_count == 0:
        feedback.insert(0, ("STATS_NONE_CORRECT", {}))
    else:
        feedback.insert(0, ("STATS_PARTIAL", {"correct": correct_count}))
    
    return score, feedback
