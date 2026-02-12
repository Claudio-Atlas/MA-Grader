# Income Analysis - Expected Formulas

## Slope & Intercept

### B30 - Slope
```
=SLOPE(B19:B26,A19:A26)
```
- Arguments: (Y_values, X_values)
- Y = Income (B19:B26)
- X = Years Experience (A19:A26)

### B31 - Intercept
```
=INTERCEPT(B19:B26,A19:A26)
```
- Arguments: (Y_values, X_values)
- Same ranges as SLOPE

### Common Mistakes
- **Reversed**: `=SLOPE(A19:A26,B19:B26)` — X and Y swapped (4/6 pts)
- **Wrong range**: Different row numbers
- **Missing**: No formula at all

---

## Predictions (E19-E35)

### Expected Pattern
```
=B30*D[row]+B31
```
or equivalently:
```
=$B$30*D[row]+$B$31
```

### Examples
- E19: `=B30*D19+B31`
- E20: `=B30*D20+B31`
- E35: `=B30*D35+B31`

### Requirements
1. Must reference B30 (slope)
2. Must reference B31 (intercept)
3. Calculated value must be correct

### Normalization
During grading, formulas are normalized:
- Remove `$` (absolute refs)
- Remove spaces
- Remove parentheses
- Convert to uppercase
