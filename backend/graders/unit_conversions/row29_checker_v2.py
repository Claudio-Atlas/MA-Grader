# graders/unit_conversions/row29_checker_v2.py

from graders.unit_conversions.utils import norm_formula, norm_unit


def grade_row_29_v2(sheet):
    """
    V2 JSON-driven strict grader for Row 29.

    Requirements:
      - Accepts these normalized units: ft/mi, yr/d, d/h
      - Accepts hr→h, day→d, year→yr in normalization
      - Each ratio formula scored independently (2 pts each)
      - Each unit scored independently (1 pt each)
      - Final formula must multiply C29, F29, I29, L29 and use '*'
      - Final unit must normalize to: 'ft/h' OR 'ft/hr'
    """

    # ---------------------- Score buckets ----------------------
    formulas_score = 0         # Max 6 (3 ratios * 2 pts)
    unit_text_score = 0        # Max 3
    final_formula_score = 0    # Max 2
    final_unit_score = 0       # Max 1

    # ---------------------- Feedback buckets ----------------------
    formulas_feedback = []
    unit_text_feedback = []
    final_formula_feedback = []
    final_unit_feedback = []

    # ---------------------- Valid formulas ----------------------
    ratio_formulas = {
        "ft/mi": {"=L21/I21", "=L21", "=L21/1"},
        "yr/d":  {"=I23/L23", "=1/L23"},
        "d/h":   {"=I22/L22", "=1/L22"}
    }

    accepted_units = {"ft/mi", "yr/d", "d/h"}

    # ---------------------- Normalize helper ----------------------
    def normalize_time_unit(u):
        if not isinstance(u, str):
            return ""
        u = u.replace("hr", "h")
        u = u.replace("day", "d")
        u = u.replace("year", "yr")
        u = u.replace("y/", "yr/")   # If they wrote y/d → yr/d
        return u

    # ---------------------- Normalize formulas ----------------------
    F = norm_formula(sheet["F29"].value)
    I = norm_formula(sheet["I29"].value)
    L = norm_formula(sheet["L29"].value)
    O = norm_formula(sheet["O29"].value)

    # ---------------------- Normalize units ----------------------
    G = normalize_time_unit(norm_unit(sheet["G29"].value))
    J = normalize_time_unit(norm_unit(sheet["J29"].value))
    M = normalize_time_unit(norm_unit(sheet["M29"].value))
    P = normalize_time_unit(norm_unit(sheet["P29"].value))

    # ---------------------- Pair structure ----------------------
    pairs = [
        ("F29", F, "G29", G),
        ("I29", I, "J29", J),
        ("L29", L, "M29", M)
    ]

    used_ratios = set()

    # ============================================================
    # 1. Evaluate three formula/unit pairs
    # ============================================================

    for f_cell, f_val, u_cell, u_val in pairs:

        # ----- UNIT CHECK -----
        if u_val in accepted_units:
            unit_text_score += 1
            unit_text_feedback.append((
                "UC29_UNIT_CORRECT",
                {"cell": u_cell, "unit": u_val}
            ))
        else:
            unit_text_feedback.append((
                "UC29_UNIT_INCORRECT",
                {"cell": u_cell, "expected": list(accepted_units)}
            ))

        # ----- FORMULA CHECK -----
        matched = False
        for ratio, forms in ratio_formulas.items():
            if f_val in forms and ratio not in used_ratios:
                formulas_score += 2
                used_ratios.add(ratio)
                matched = True
                formulas_feedback.append((
                    "UC29_FORMULA_CORRECT",
                    {"cell": f_cell, "ratio": ratio}
                ))
                break

        if not matched:
            formulas_feedback.append((
                "UC29_FORMULA_INCORRECT",
                {"cell": f_cell}
            ))

    # ============================================================
    # 2. Final formula check — O29
    # ============================================================

    required_refs = ["C29", "F29", "I29", "L29"]

    if all(ref in O for ref in required_refs) and "*" in O:
        final_formula_score = 2
        final_formula_feedback.append((
            "UC29_FINAL_FORMULA_CORRECT",
            {"cell": "O29"}
        ))
    else:
        final_formula_feedback.append((
            "UC29_FINAL_FORMULA_INCORRECT",
            {"cell": "O29", "required": required_refs}
        ))

    # ============================================================
    # 3. Final unit check — P29
    # ============================================================

    if P in {"ft/h", "ft/hr"}:
        final_unit_score = 1
        final_unit_feedback.append((
            "UC29_FINAL_UNIT_CORRECT",
            {"cell": "P29", "unit": P}
        ))
    else:
        final_unit_feedback.append((
            "UC29_FINAL_UNIT_INCORRECT",
            {"cell": "P29", "expected": "ft/h or ft/hr"}
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
        "final_unit_feedback": final_unit_feedback
    }
