# graders/currency_conversion_v2/row20_budget_conversion_v2.py

from ..currency_conversion.utils import norm_unit


def grade_row20_budget_conversion_v2(sheet):
    """
    Currency Conversion V2 - Row 20 (C20-F20)

    Rule (same as V1):
      - Each cell must multiply B4 by corresponding exchange rate cell:
          C20 = B4*C19 (or C19*B4)
          D20 = B4*D19 (or D19*B4)
          E20 = B4*E19 (or E19*B4)
          F20 = B4*F19 (or F19*B4)

    Scoring:
      - Formula correctness: 2.0 pts per cell (max 8.0)
      - Formatting correctness: 0.25 pts per cell (max 1.0)
      - Total possible: 9.0

    Returns:
      (total_score, formula_score, format_score, feedback)
        feedback is list[(code, params)]
    """

    pairs = [("C20", "C19"), ("D20", "D19"), ("E20", "E19"), ("F20", "F19")]

    formula_score = 0.0
    format_score = 0.0
    feedback = []

    for target_cell, rate_ref in pairs:
        raw_formula = sheet[target_cell].value

        # -----------------------------
        # Formula must exist
        # -----------------------------
        if not isinstance(raw_formula, str) or not raw_formula.startswith("="):
            feedback.append(("CC20_FORMULA_MISSING", {"cell": target_cell, "rate_ref": rate_ref}))
        else:
            f = norm_unit(raw_formula)  # your existing normalizer (lowercases & strips)

            valid_1 = f == f"=b4*{rate_ref.lower()}"
            valid_2 = f == f"={rate_ref.lower()}*b4"

            if valid_1 or valid_2:
                formula_score += 2.0
                feedback.append(("CC20_FORMULA_OK", {"cell": target_cell, "rate_ref": rate_ref}))
            else:
                feedback.append((
                    "CC20_FORMULA_BAD",
                    {"cell": target_cell, "rate_ref": rate_ref, "expected_a": f"=B4*{rate_ref}", "expected_b": f"={rate_ref}*B4"}
                ))

        # -----------------------------
        # Formatting: Currency with 2 decimals
        # (same acceptance logic as V1)
        # -----------------------------
        num_fmt = str(sheet[target_cell].number_format).lower()
        if "$" in num_fmt or "currency" in num_fmt or "0.00" in num_fmt:
            format_score += 0.25
            feedback.append(("CC20_FORMAT_OK", {"cell": target_cell}))
        else:
            feedback.append(("CC20_FORMAT_BAD", {"cell": target_cell}))

    total_score = round(formula_score + format_score, 2)

    feedback.insert(0, (
        "CC20_SUMMARY",
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
