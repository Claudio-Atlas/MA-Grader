# graders/income_analysis/check_predictions_formatting.py

def _is_currency_zero_decimal(fmt: str) -> bool:
    """
    Check if a number format is currency with 0 decimal places.
    More flexible than exact string matching.
    """
    if not fmt or not isinstance(fmt, str):
        return False
    
    # Must contain $ somewhere (currency indicator)
    if "$" not in fmt:
        return False
    
    # Should NOT have decimal places (no .0 or .00)
    if ".0" in fmt or ".#" in fmt:
        return False
    
    # Must have number placeholders
    if "0" not in fmt and "#" not in fmt:
        return False
    
    return True


def check_currency_formatting(ws):
    """
    Check formatting of predicted values E19-E35.
    Expected: currency with 0 decimal places.

    Returns:
        (score: float, feedback: list[tuple[str, dict]])
    """
    total_rows = 17
    correct_count = 0
    sample_incorrect_fmt = None

    for row in range(19, 36):
        cell = ws[f"E{row}"]
        fmt = cell.number_format
        if _is_currency_zero_decimal(fmt):
            correct_count += 1
        elif sample_incorrect_fmt is None:
            sample_incorrect_fmt = fmt

    if correct_count == total_rows:
        return 1.0, [("IA_PRED_FORMAT_ALL_CORRECT", {"range": "E19:E35"})]

    if correct_count == 0:
        return 0.0, [("IA_PRED_FORMAT_NONE_CORRECT", {"range": "E19:E35", "found": sample_incorrect_fmt})]

    score = round(correct_count / total_rows, 2)
    return score, [("IA_PRED_FORMAT_PARTIAL", {"correct": correct_count, "total": total_rows, "range": "E19:E35"})]
