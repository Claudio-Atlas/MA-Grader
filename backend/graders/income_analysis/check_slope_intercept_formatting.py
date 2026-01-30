# graders/income_analysis/check_slope_intercept_formatting.py

def _is_zero_decimal_number_format(fmt: str) -> bool:
    """
    Check if a number format displays numbers with 0 decimal places.
    More flexible than exact string matching.
    """
    if not fmt or not isinstance(fmt, str):
        return False
    
    # Normalize: lowercase, strip whitespace
    fmt = fmt.strip()
    
    # Exact matches for common formats
    allowed_exact = {
        "0",
        "0_",
        "0_)",
        "#,##0",
        "#,##0_",
        "#,##0_)",
        "0;-0;0",
        "#,##0;-#,##0;0",
        "#,##0;-#,##0",
        "#,##0_);(#,##0)",
        "#,##0_);[Red](#,##0)",
        "0_);(0)",
        "0_);[Red](0)",
        "General",  # General often displays as integer for whole numbers
    }
    
    if fmt in allowed_exact:
        return True
    
    # Pattern-based check: should have 0s but no decimal places
    # Reject anything with .0, .00, etc.
    if ".0" in fmt or ".#" in fmt:
        return False
    
    # Accept if it contains number placeholders (0 or #) and no decimals
    has_number_chars = "0" in fmt or "#" in fmt
    if has_number_chars:
        return True
    
    return False


def check_slope_intercept_formatting(ws):
    """
    Checks formatting of B30 (slope) and B31 (intercept).
    Correct formatting = number format with 0 decimal places.

    Returns:
        (score: float from 0 to 1,
         feedback: list[tuple[str, dict]])
    """
    slope_cell = ws["B30"]
    intercept_cell = ws["B31"]

    slope_fmt = slope_cell.number_format
    intercept_fmt = intercept_cell.number_format

    score = 0.0
    feedback = []

    if _is_zero_decimal_number_format(slope_fmt):
        score += 0.5
        feedback.append(("IA_SLOPE_FORMAT_CORRECT", {"cell": "B30"}))
    else:
        feedback.append(("IA_SLOPE_FORMAT_INCORRECT", {"cell": "B30", "found": slope_fmt}))

    if _is_zero_decimal_number_format(intercept_fmt):
        score += 0.5
        feedback.append(("IA_INTERCEPT_FORMAT_CORRECT", {"cell": "B31"}))
    else:
        feedback.append(("IA_INTERCEPT_FORMAT_INCORRECT", {"cell": "B31", "found": intercept_fmt}))

    return score, feedback
