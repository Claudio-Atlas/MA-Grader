# MA1 Grader - Known Edge Cases

## Country Selection (Row 16)

### No Country for Letter X
- **Problem**: No country starts with X
- **Solution**: Fallback to next available letter (Y → Yemen)
- **Affected**: Students with X in first/last name (e.g., "Alexander" 2nd letter, "Cox" 2nd letter)

### Limited Countries for O, Q, W, Y, Z
- O: Oman only
- Q: Qatar only  
- W: Wallis and Futuna only
- Y: Yemen only
- Z: Zambia only
- **Solution**: These still work (one option is enough)

---

## Slope & Intercept

### X and Y Data Swapped
- **Problem**: Student uses `=SLOPE(A19:A26,B19:B26)` instead of `=SLOPE(B19:B26,A19:A26)`
- **Solution**: Give 2/3 pts per formula (4/6 total for formulas)
- **Feedback**: `IA_XY_DATA_SWAPPED` explains the issue

### Slope and Intercept in Wrong Cells
- **Problem**: Student puts INTERCEPT formula in B30 and SLOPE in B31
- **Solution**: TBD (currently not explicitly handled)

---

## Temperature Conversions

### Correct Value, No Cell References
- **Problem**: Student types formula like `=(5/9)*(72-32)` instead of `=(5/9)*(A40-32)`
- **Solution**: Partial credit (1/2 pts) if calculated value is correct
- **Added**: 2025-01-30

---

## Predictions (E19-E35)

### Hard-coded Values
- **Problem**: Student types numbers instead of formulas
- **Solution**: Check for BOTH B30/B31 refs AND correct value — must have both

### Alternative Formula Order
- **Problem**: `=B31+B30*D19` vs `=B30*D19+B31`
- **Solution**: Currently requires exact match — may need flexibility

---

## Formatting False Positives

### Issue
Some formatting looks correct visually but fails the check.

### Common Causes
- Regional format variants
- Negative number formatting (red, parentheses)
- Trailing underscores or alignment characters

### Solution (2025-01-30)
Made formatting checks pattern-based instead of exact-match:
- Number with 0 decimals: Has `0` or `#`, no `.0` or `.#`
- Currency with 0 decimals: Has `$`, has number chars, no decimals

---

## Name Extraction (Row 15)

### AI-Like Behavior
- **Observation**: Using complex formulas to extract single letters seems AI-generated
- **Example**: Julia Johnson case
- **Decision**: Keep as-is for now, but flag for manual review if suspicious
