# graders/unit_conversions/row27_checker_v2.py

from graders.unit_conversions.utils import norm_formula, norm_unit


def grade_row_27_v2(sheet):
    """
    V2 JSON-driven strict grader for Row 27.

    Requirements:
      - Accepts gal/l and h/d conversions
      - hr -> h normalization
      - day -> d normalization
      - Each F27/I27 cell graded independently
      - Final formula must include: C27, F27, I27 and use '*'
      - Final unit must normalize to exactly 'gal/d'
    """

    # -------------- Score buckets --------------
    formulas_score = 0       # 4 points max (2 + 2)
    unit_text_score = 0      # 2 points max
    final_formula_score = 0  # 2 points max
    final_unit_score = 0     # 1 point max

    # -------------- Feedback buckets --------------
    formulas_feedback = []
    unit_text_feedback = []
    final_formula_feedback = []
    final_unit_feedback = []

    # -------------------------------------------------------
    # 1. VALID FORMULAS FOR ROW 27
    # -------------------------------------------------------
    ratio_options = {
        "gal/l": {"=L16/I16", "=L16", "=L16/1"},
        "h/d":   {"=L22/I22", "=L22", "=L22/1"}
    }

    valid_units = {"gal/l", "h/d"}

    # -------------------------------------------------------
    # 2. Pull + Normalize Data
    # -------------------------------------------------------

    # Normalize formulas
    F = norm_formula(sheet["F27"].value)
    I = norm_formula(sheet["I27"].value)
    O = norm_formula(sheet["O27"].value)

    # Normalize unit text (including hr->h, day->d normalization)
    def normalize_time(u):
        u = u.replace("hr", "h")
        u = u.replace("day", "d")
        return u

    G = normalize_time(norm_unit(sheet["G27"].value))
    J = normalize_time(norm_unit(sheet["J27"].value))
    P = normalize_time(norm_unit(sheet["P27"].value))

    # -------------------------------------------------------
    # 3. Check Formula + Unit Rules for F27 and I27
    # -------------------------------------------------------

    pairs = [
        ("F27", F, "G27", G),
        ("I27", I, "J27", J)
    ]

    for formula_cell, formula_val, unit_cell, unit_val in pairs:

        # ----- UNIT CHECK -----
        if unit_val in valid_units:
            unit_text_score += 1
            unit_text_feedback.append((
                "UC27_UNIT_CORRECT",
                {"cell": unit_cell, "unit": unit_val}
            ))
        else:
            unit_text_feedback.append((
                "UC27_UNIT_INCORRECT",
                {"cell": unit_cell, "expected": list(valid_units)}
            ))

        # ----- FORMULA CHECK -----
        matched = False
        for ratio, valid_forms in ratio_options.items():
            if formula_val in valid_forms:
                formulas_score += 2
                matched = True
                formulas_feedback.append((
                    "UC27_FORMULA_CORRECT",
                    {"cell": formula_cell, "ratio": ratio}
                ))
                break

        if not matched:
            formulas_feedback.append((
                "UC27_FORMULA_INCORRECT",
                {"cell": formula_cell}
            ))

    # -------------------------------------------------------
    # 4. Final formula check - O27
    # -------------------------------------------------------

    required_refs = ["C27", "F27", "I27"]

    if all(ref in O for ref in required_refs) and "*" in O:
        final_formula_score = 2
        final_formula_feedback.append((
            "UC27_FINAL_FORMULA_CORRECT",
            {"cell": "O27"}
        ))
    else:
        final_formula_feedback.append((
            "UC27_FINAL_FORMULA_INCORRECT",
            {"cell": "O27", "required": required_refs}
        ))

    # -------------------------------------------------------
    # 5. Final unit check - P27
    # -------------------------------------------------------

    if P == "gal/d":  # strict
        final_unit_score = 1
        final_unit_feedback.append((
            "UC27_FINAL_UNIT_CORRECT",
            {"cell": "P27", "unit": P}
        ))
    else:
        final_unit_feedback.append((
            "UC27_FINAL_UNIT_INCORRECT",
            {"cell": "P27", "expected": "gal/d"}
        ))

    # -------------------------------------------------------
    # 6. Return V2 structure
    # -------------------------------------------------------

    return {
        "formulas_score": formulas_score,
        "unit_text_score": unit_text_score,
        "final_formula_score": final_formula_score,
        "final_unit_score": final_unit_score,

        "formulas_feedback": formulas_feedback,
        "unit_text_feedback": unit_text_feedback,
        "final_formula_feedback": final_formula_feedback,
        "final_unit_feedback": final_unit_feedback
    }
