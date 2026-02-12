# Currency Conversion - Expected Formulas

## Row 20 - Budget Conversion

### Expected Pattern
```
=B4*[rate_cell]
```
or
```
=[rate_cell]*B4
```

### Examples
- C20: `=B4*C19` or `=C19*B4`
- D20: `=B4*D19` or `=D19*B4`
- E20: `=B4*E19` or `=E19*B4`
- F20: `=B4*F19` or `=F19*B4`

---

## Row 21 - USD Conversion Back

### Expected Pattern
```
=D4/[rate_cell]
```

### Examples
- C21: `=D4/C19`
- D21: `=D4/D19`
- E21: `=D4/E19`
- F21: `=D4/F19`

---

## Key Cells

| Cell | Content |
|------|---------|
| B4 | Budget amount (USD) |
| D4 | Foreign amount to convert back |
| C19-F19 | Exchange rates |
| C20-F20 | Budget in foreign currency |
| C21-F21 | Foreign amount back to USD |
