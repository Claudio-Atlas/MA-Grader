# graders/currency_conversion_v2/row21_usd_conversion_back_v2.py

import re


def _normalize_formula(formula):
    """
    Normalize an Excel formula string for comparison:
      - removes leading '='
      - strips $, spaces, parentheses
      - lowercase
    """
    if not isinstance(formula, str):
        return ""
    f = formula.lstrip("=")
    f = f.replace("$", "")
    f = re.sub(r"[()\s]", "", f)
    return f.lower()


def grade_row21_usd_conversion_back_v2(sheet):
    """
    Currency Conversion V2 - Row 21 (C21-F21)

    Rule (same as V1):
      Converts foreign amount (D4) back to USD using the corresponding rate in row 19:
        C21 = D4 / C19
        D21 = D4 / D19
        E21 = D4 / E19
        F21 = D4 / F19

    Scoring:
      - Formula correctness: 2.0 pts per cell (max 8.0)
      - Formatting correctness (currency, 2 decimals): 0.25 pts per cell (max 1.0)
      - Total possible: 9.0

    Returns:
      (total_score, formula_score, format_score, feedback)
        feedback is list[(code, params)]
    """

    usd_cell = "D4"
    rate_row = 19
    row = 21
    cols = ["C", "D", "E", "F"]

    formula_score = 0.0
    format_score = 0.0
    feedback = []

    for col in cols:
        cell_ref = f"{col}{row}"
        source_rate_cell = f"{col}{rate_row}"

        raw_formula = sheet[cell_ref].value

        # -----------------------------
        # Formula check
        # -----------------------------
        if not isinstance(raw_formula, str) or not raw_formula.startswith("="):
            feedback.append(("CC21_FORMULA_MISSING", {"cell": cell_ref, "expected": f"=D4/{source_rate_cell}"}))
        else:
            cleaned = _normalize_formula(raw_formula)
            expected = _normalize_formula(f"{usd_cell}/{source_rate_cell}")

            if cleaned == expected:
                formula_score += 2.0
                feedback.append(("CC21_FORMULA_OK", {"cell": cell_ref, "expected": f"=D4/{source_rate_cell}"}))
            else:
                feedback.append(("CC21_FORMULA_BAD", {"cell": cell_ref, "expected": f"=D4/{source_rate_cell}"}))

        # -----------------------------
        # Formatting check (same acceptance logic as V1)
        # -----------------------------
        num_fmt = str(sheet[cell_ref].number_format).lower()
        if "$" in num_fmt or "currency" in num_fmt or "0.00" in num_fmt:
            format_score += 0.25
            feedback.append(("CC21_FORMAT_OK", {"cell": cell_ref}))
        else:
            feedback.append(("CC21_FORMAT_BAD", {"cell": cell_ref}))

    total_score = round(formula_score + format_score, 2)

    feedback.insert(0, (
        "CC21_SUMMARY",
        {
            "formula": round(formula_score, 2),
            "formula_possible": 8.0,
            "formatting": round(format_score, 2),
            "formatting_possible": 1.0,
            "total": total_score,
            "total_possible": 9.0
        }
    ))

    return total_score, round(formula_score, 2), round(format_score, 2), feedback
