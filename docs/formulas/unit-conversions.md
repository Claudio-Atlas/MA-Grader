# Unit Conversions - Expected Formulas

## Temperature Conversions

### C40 - Fahrenheit to Celsius
```
=(5/9)*(A40-32)
```

**Required fragments:**
- `5/9` — conversion factor
- `A40-32` — cell reference minus 32

**Equivalent forms:**
- `=(A40-32)*(5/9)`
- `=5/9*(A40-32)`
- `=(A40-32)*5/9`

### A41 - Celsius to Fahrenheit
```
=(9/5)*C41+32
```

**Required fragments:**
- `9/5` — conversion factor
- `C41` — cell reference
- `+32` — addition of 32

**Equivalent forms:**
- `=C41*9/5+32`
- `=C41*(9/5)+32`
- `=9/5*C41+32`

---

## Scoring

| Scenario | Points |
|----------|--------|
| Formula with cell refs | 2/2 |
| Formula, correct value, no cell refs | 1/2 |
| No formula or wrong value | 0/2 |

---

## Key Cells

| Cell | Content |
|------|---------|
| A40 | Fahrenheit input value |
| C40 | Celsius result (calculated) |
| C41 | Celsius input value |
| A41 | Fahrenheit result (calculated) |
