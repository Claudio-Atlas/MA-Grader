# graders/unit_conversions/row28_checker_v2.py

from graders.unit_conversions.utils import norm_formula, norm_unit


def grade_row_28_v2(sheet):
    """
    V2 JSON-driven strict grader for Row 28.

    Requirements:
      - Row 28 uses THREE conversion ratios:
          1. kg/lb   (F/L columns)
          2. in/cm   (F/I/L columns depending on student order)
      - Each ratio formula scored independently (2 pts each)
      - Each unit label scored independently (1 pt each)
      - Final formula must multiply C28, F28, I28, L28 (in any order)
      - Final unit must be exactly 'kg/cm^2'
    """

    # ---------------------- Score buckets ----------------------
    formulas_score = 0        # Max 6 (2*3 ratios)
    unit_text_score = 0       # Max 3
    final_formula_score = 0   # Max 2
    final_unit_score = 0      # Max 1

    # ---------------------- Feedback buckets ----------------------
    formulas_feedback = []
    unit_text_feedback = []
    final_formula_feedback = []
    final_unit_feedback = []

    # ---------------------- Valid formulas ----------------------
    ratio_options = {
        "kg/lb": {"=I9/L9", "=1/L9"},
        "in/cm": {"=I20/L20", "=1/L20"}
    }

    accepted_units = {"kg/lb", "in/cm"}

    # ---------------------- Normalize inputs ----------------------
    F = norm_formula(sheet["F28"].value)
    G = norm_unit(sheet["G28"].value)

    I = norm_formula(sheet["I28"].value)
    J = norm_unit(sheet["J28"].value)

    L = norm_formula(sheet["L28"].value)
    M = norm_unit(sheet["M28"].value)

    O = norm_formula(sheet["O28"].value)
    P = norm_unit(sheet["P28"].value)

    # For looping over 3 independent pairs
    pairs = [
        ("F28", F, "G28", G),
        ("I28", I, "J28", J),
        ("L28", L, "M28", M)
    ]

    # Track usage to ensure a ratio cannot get double-counted
    ratio_usage = {"kg/lb": 0, "in/cm": 0}
    unit_usage = {"kg/lb": 0, "in/cm": 0}

    # ============================================================
    # 1. Evaluate the three formula/unit pairs independently
    # ============================================================

    for formula_cell, formula_val, unit_cell, unit_val in pairs:

        # ----- UNIT CHECK -----
        if unit_val in accepted_units:
            unit_text_score += 1
            unit_text_feedback.append((
                "UC28_UNIT_CORRECT",
                {"cell": unit_cell, "unit": unit_val}
            ))
            unit_usage[unit_val] += 1
        else:
            unit_text_feedback.append((
                "UC28_UNIT_INCORRECT",
                {"cell": unit_cell, "expected": list(accepted_units)}
            ))

        # ----- FORMULA CHECK -----
        matched_formula = False
        for ratio, valid_forms in ratio_options.items():
            if formula_val in valid_forms:
                formulas_score += 2
                matched_formula = True
                ratio_usage[ratio] += 1
                formulas_feedback.append((
                    "UC28_FORMULA_CORRECT",
                    {"cell": formula_cell, "ratio": ratio}
                ))
                break

        if not matched_formula:
            formulas_feedback.append((
                "UC28_FORMULA_INCORRECT",
                {"cell": formula_cell}
            ))

    # ============================================================
    # 2. Final Formula Check (O28)
    # ============================================================

    required_refs = ["C28", "F28", "I28", "L28"]

    if all(ref in O for ref in required_refs) and "*" in O:
        final_formula_score = 2
        final_formula_feedback.append((
            "UC28_FINAL_FORMULA_CORRECT",
            {"cell": "O28"}
        ))
    else:
        final_formula_feedback.append((
            "UC28_FINAL_FORMULA_INCORRECT",
            {"cell": "O28", "required": required_refs}
        ))

    # ============================================================
    # 3. Final Unit Check (P28)
    # ============================================================

    if P == "kg/cm^2":
        final_unit_score = 1
        final_unit_feedback.append((
            "UC28_FINAL_UNIT_CORRECT",
            {"cell": "P28", "unit": P}
        ))
    else:
        final_unit_feedback.append((
            "UC28_FINAL_UNIT_INCORRECT",
            {"cell": "P28", "expected": "kg/cm^2"}
        ))

    # ============================================================
    # 4. Return V2 structure
    # ============================================================

    return {
        "formulas_score": formulas_score,
        "unit_text_score": unit_text_score,
        "final_formula_score": final_formula_score,
        "final_unit_score": final_unit_score,

        "formulas_feedback": formulas_feedback,
        "unit_text_feedback": unit_text_feedback,
        "final_formula_feedback": final_formula_feedback,
        "final_unit_feedback": final_unit_feedback,

        # Debug info (optional but useful)
        "debug_usage": {
            "ratio_usage": ratio_usage,
            "unit_usage": unit_usage
        }
    }
