# MA-Grader Brain 🧠

This folder contains reference documentation for the MA1 Major Assignments Grader.

## Contents

| File | Purpose |
|------|---------|
| `RUBRIC.md` | Complete grading rubric with point values |
| `EDGE-CASES.md` | Known edge cases and how they're handled |
| `STUDENT-FEEDBACK.md` | Log of student complaints and resolutions |
| `CHANGELOG.md` | History of grader changes |
| `formulas/` | Expected Excel formulas by section |

## Quick Reference

### Grader Location
```
/Users/claudioatlas/Desktop/MA-Grader/backend/graders/
```

### Main Modules
- `currency_conversion/` — Currency Conversion tab graders
- `income_analysis/` — Income Analysis tab graders  
- `unit_conversions/` — Unit Conversions tab graders

### Key Files (frequently edited)
- `row16_country_selection_v2.py` — Country name validation
- `check_slope_intercept.py` — SLOPE/INTERCEPT formulas
- `check_predictions.py` — Prediction formula validation
- `temp_conversions_v2.py` — Temperature conversion formulas

## Usage

When debugging grading issues:
1. Check `EDGE-CASES.md` — might already be documented
2. Check `STUDENT-FEEDBACK.md` — similar complaint may exist
3. Check `formulas/` — verify expected vs actual formula
4. Update `CHANGELOG.md` after making changes

---

*Created 2025-01-30 by Claudio*
