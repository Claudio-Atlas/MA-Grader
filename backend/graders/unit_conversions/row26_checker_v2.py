# graders/unit_conversions/row26_checker_v2.py

from graders.unit_conversions.utils import norm_formula, norm_unit


def grade_row_26_v2(sheet):
    """
    V2 JSON-driven strict grader for Row 26.
    Requires exactly one mcg/mg ratio and exactly one ml/tsp ratio,
    in either order between F26/I26. No duplicates allowed.
    """

    # -------------- Scoring buckets --------------
    formulas_score = 0        # 4 points max (2 per required ratio)
    unit_text_score = 0       # 2 points max
    final_formula_score = 0   # 2 points max
    final_unit_score = 0      # 1 point max

    # -------------- Feedback buckets --------------
    formulas_feedback = []        # list of (code, params)
    unit_text_feedback = []
    final_formula_feedback = []
    final_unit_feedback = []

    # -------------- Accepted ratio patterns --------------
    mcg_mg_forms = {"=L14/I14", "=L14", "=L14/1"}
    ml_tsp_forms = {"=L17/I17", "=L17", "=L17/1"}

    # -------------- Normalize inputs --------------
    F = norm_formula(sheet["F26"].value)
    G = norm_unit(sheet["G26"].value)
    I = norm_formula(sheet["I26"].value)
    J = norm_unit(sheet["J26"].value)
    O = norm_formula(sheet["O26"].value)
    P = norm_unit(sheet["P26"].value)

    # -------------- Row 26 Accepted Units --------------
    valid_units = {"mcg/mg", "ml/tsp"}

    # Track usage for STRICT enforcement
    found_mcg = False
    found_ml = False

    # ==========================================================
    # 1. UNIT LABEL CHECKS
    # ==========================================================

    # --- G26 ---
    if G in valid_units:
        unit_text_score += 1
        unit_text_feedback.append(("UC26_UNIT_VALID_G", {"cell": "G26", "unit": G}))
    else:
        unit_text_feedback.append(("UC26_UNIT_INVALID_G",
                                   {"cell": "G26", "expected": list(valid_units)}))

    # --- J26 ---
    if J in valid_units:
        unit_text_score += 1
        unit_text_feedback.append(("UC26_UNIT_VALID_J", {"cell": "J26", "unit": J}))
    else:
        unit_text_feedback.append(("UC26_UNIT_INVALID_J",
                                   {"cell": "J26", "expected": list(valid_units)}))

    # ==========================================================
    # 2. FORMULA CHECKS — STRICT (Option A)
    # ==========================================================

    # ----- F26 -----
    if F in mcg_mg_forms and not found_mcg:
        formulas_score += 2
        found_mcg = True
        formulas_feedback.append(("UC26_FORMULA_F_VALID",
                                  {"cell": "F26", "ratio": "mcg/mg"}))

    elif F in ml_tsp_forms and not found_ml:
        formulas_score += 2
        found_ml = True
        formulas_feedback.append(("UC26_FORMULA_F_VALID",
                                  {"cell": "F26", "ratio": "ml/tsp"}))

    else:
        formulas_feedback.append(("UC26_FORMULA_F_INVALID",
                                  {"cell": "F26"}))

    # ----- I26 -----
    if I in mcg_mg_forms and not found_mcg:
        formulas_score += 2
        found_mcg = True
        formulas_feedback.append(("UC26_FORMULA_I_VALID",
                                  {"cell": "I26", "ratio": "mcg/mg"}))

    elif I in ml_tsp_forms and not found_ml:
        formulas_score += 2
        found_ml = True
        formulas_feedback.append(("UC26_FORMULA_I_VALID",
                                  {"cell": "I26", "ratio": "ml/tsp"}))

    else:
        formulas_feedback.append(("UC26_FORMULA_I_INVALID",
                                  {"cell": "I26"}))

    # STRICT enforcement:
    # Must end with exactly one mcg/mg AND one ml/tsp.
    # If duplicates occurred, feedback already added above.

    # ==========================================================
    # 3. FINAL FORMULA CHECK (O26)
    # ==========================================================

    required_refs = ["C26", "F26", "I26"]

    if all(ref in O for ref in required_refs) and "*" in O:
        final_formula_score = 2
        final_formula_feedback.append(("UC26_FINAL_FORMULA_CORRECT",
                                       {"cell": "O26"}))
    else:
        final_formula_feedback.append(("UC26_FINAL_FORMULA_INCORRECT",
                                       {"cell": "O26",
                                        "required": required_refs}))

    # ==========================================================
    # 4. FINAL UNIT CHECK (P26)
    # ==========================================================

    if P == "mcg/tsp":
        final_unit_score = 1
        final_unit_feedback.append(("UC26_FINAL_UNIT_CORRECT",
                                    {"cell": "P26", "unit": P}))
    else:
        final_unit_feedback.append(("UC26_FINAL_UNIT_INCORRECT",
                                    {"cell": "P26", "expected": "mcg/tsp"}))

    # ==========================================================
    # RETURN V2 STRUCTURE
    # ==========================================================

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
