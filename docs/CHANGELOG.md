# MA-Grader Changelog

## 2025-01-30

### Country Selection Fallback
- **File**: `graders/currency_conversion/row16_country_selection_v2.py`
- **Change**: Added `_get_fallback_letter()` function
- **Details**: If expected letter has no countries (X), falls back to next available (Y)
- **Reason**: Students with X in name couldn't fulfill requirement

### Predictions Dual-Check
- **File**: `graders/income_analysis/check_predictions.py`
- **Change**: Now requires BOTH cell refs (B30/B31) AND correct calculated value
- **Details**: 
  - Added `_has_required_refs()` — checks for B30 AND B31 (case-insensitive)
  - Added `_calculate_expected_value()` — computes expected from slope/intercept
  - Added `_get_cell_calculated_value()` — gets cell's numeric value
- **Reason**: Prevent students from typing hard-coded numbers

### X-Y Swap Feedback
- **File**: `graders/income_analysis/check_slope_intercept.py`
- **Change**: Added `IA_XY_DATA_SWAPPED` feedback code
- **Details**: When both slope and intercept have reversed arguments, adds summary feedback
- **Reason**: Make it clearer why points were deducted

### Temperature Partial Credit
- **File**: `graders/unit_conversions/temp_conversions_v2.py`
- **Change**: Added partial credit for correct value without cell refs
- **Details**:
  - Full credit (2 pts): Formula with cell refs
  - Partial credit (1 pt): Formula with correct value, no cell refs
  - New codes: `UC_TEMP_C40_PARTIAL`, `UC_TEMP_A41_PARTIAL`
- **Reason**: Was giving 0 for correct answers just missing refs

### Flexible Formatting Checks
- **Files**: 
  - `graders/income_analysis/check_slope_intercept_formatting.py`
  - `graders/income_analysis/check_predictions_formatting.py`
- **Change**: Pattern-based format checking instead of exact-match
- **Details**:
  - `_is_zero_decimal_number_format()` — accepts formats with 0/#, no decimals
  - `_is_currency_zero_decimal()` — accepts formats with $, no decimals
  - Feedback now includes actual format found when incorrect
- **Reason**: Some valid formats were being rejected

---

## Template

### [Feature Name]
- **File**: 
- **Change**: 
- **Details**: 
- **Reason**: 
