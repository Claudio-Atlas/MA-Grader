# MA1 Grading Rubric

## Currency Conversion Tab

### Row 15 - Name Letters (via formula)
- C15-F15: Extract letters from student name
- Points: TBD
- Note: Using formulas for letters is expected, but suspicious if overly complex

### Row 16 - Country Selection (2 pts total)
- C16, D16: Country starting with 1st and 2nd letter of FIRST name
- E16, F16: Country starting with 1st and 2nd letter of LAST name
- 0.5 pts per cell
- **Edge case**: Letter X has no countries → falls back to Y (Yemen)
- Limited letters (one country each): O (Oman), Q (Qatar), W (Wallis/Futuna), Y (Yemen), Z (Zambia)

### Row 17 - Date Entries
- TBD

### Row 18 - Currency Codes
- C18-F18: Must match country's currency code
- Points: TBD

### Row 19 - Exchange Rates (5 pts total)
- C19-F19: USD exchange rates for each currency
- Accuracy: 1 pt each (within ±5% of live rate) = 4 pts max
- Formatting: 0.25 pts each (3 decimal places) = 1 pt max

### Row 20 - Budget Conversion (9 pts total)
- C20-F20: `=B4*[rate cell]` or `=[rate cell]*B4`
- Formula: 2 pts each = 8 pts max
- Formatting: 0.25 pts each (currency, 2 decimals) = 1 pt max

### Row 21 - USD Conversion Back (9 pts total)
- C21-F21: `=D4/[rate cell]`
- Formula: 2 pts each = 8 pts max
- Formatting: 0.25 pts each (currency, 2 decimals) = 1 pt max

---

## Unit Conversions Tab

### Temperature Conversions (4 pts total)
- C40: Fahrenheit to Celsius `=(5/9)*(A40-32)` — 2 pts
- A41: Celsius to Fahrenheit `=(9/5)*C41+32` — 2 pts
- **Partial credit**: Correct value but no cell refs → 1 pt each (2/4 max)

### Other Unit Conversions
- Rows 26-29: Various conversions
- 1 pt per correct unit label

---

## Income Analysis Tab

### Name Present
- Row 3: Student name
- Points: TBD

### Slope & Intercept (7 pts total)
- B30: `=SLOPE(B19:B26,A19:A26)` — 3 pts
- B31: `=INTERCEPT(B19:B26,A19:A26)` — 3 pts
- Formatting (0 decimals): 0.5 pts each = 1 pt
- **X-Y Reversed**: `=SLOPE(A19:A26,B19:B26)` → 2 pts each (4/6 for formulas, -2 penalty)

### Predictions (7 pts total)
- E19-E35: `=B30*D[row]+B31` — 6 pts (17 rows)
- **Must have**: B30 AND B31 cell refs + correct calculated value
- Formatting (currency, 0 decimals): 1 pt

### Scatterplot
- Manual grading required

---

## General Rules

- Cell references are case-insensitive (B30 = b30)
- Formulas must start with `=`
- Spacing and `$` are normalized out during comparison
