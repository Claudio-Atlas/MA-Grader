# graders/unit_conversions/unit_conversions_checker_v2.py

from graders.unit_conversions.row26_checker_v2 import grade_row_26_v2
from graders.unit_conversions.row27_checker_v2 import grade_row_27_v2
from graders.unit_conversions.row28_checker_v2 import grade_row_28_v2
from graders.unit_conversions.row29_checker_v2 import grade_row_29_v2
from graders.unit_conversions.temp_conversions_v2 import grade_temp_conversions_v2


def grade_unit_conversions_tab_v2(sheet):
    """
    Orchestrates grading for the entire Unit Conversions tab using the V2 system.

    Rows:
      - 26: mcg/mg & mL/tsp conversions
      - 27: gal/l & h/d conversions
      - 28: kg/lb & in/cm conversions
      - 29: ft/mi, yr/d, d/h conversions
      - Temp conversions: C40 & A41
    
    Returns:
        Unified dictionary including:
          - unit_text_score
          - formulas_score
          - final_formula_score
          - final_unit_score
          - temp_and_celsius_score
          - feedback categories for each grouping
    """

    # ------------------------
    # Run each row check
    # ------------------------
    r26 = grade_row_26_v2(sheet)
    r27 = grade_row_27_v2(sheet)
    r28 = grade_row_28_v2(sheet)
    r29 = grade_row_29_v2(sheet)
    temp = grade_temp_conversions_v2(sheet)

    # ------------------------
    # Aggregate scoring
    # ------------------------

    # Unit text score = sum of unit_text_score from rows 26-29
    unit_text_score = (
        r26["unit_text_score"]
        + r27["unit_text_score"]
        + r28["unit_text_score"]
        + r29["unit_text_score"]
    )

    # Formula score = sum of formulas_score from rows 26-29
    formulas_score = (
        r26["formulas_score"]
        + r27["formulas_score"]
        + r28["formulas_score"]
        + r29["formulas_score"]
    )

    # Final formula score = sum of O26/O27/O28/O29 checks
    final_formula_score = (
        r26["final_formula_score"]
        + r27["final_formula_score"]
        + r28["final_formula_score"]
        + r29["final_formula_score"]
    )

    # Final unit score = sum of P26/P27/P28/P29 checks
    final_unit_score = (
        r26["final_unit_score"]
        + r27["final_unit_score"]
        + r28["final_unit_score"]
        + r29["final_unit_score"]
    )

    temp_score = temp["temp_and_celsius_score"]

    # ------------------------
    # Aggregate feedback lists
    # ------------------------

    unit_text_feedback = (
          r26["unit_text_feedback"]
        + r27["unit_text_feedback"]
        + r28["unit_text_feedback"]
        + r29["unit_text_feedback"]
    )

    formulas_feedback = (
          r26["formulas_feedback"]
        + r27["formulas_feedback"]
        + r28["formulas_feedback"]
        + r29["formulas_feedback"]
    )

    final_formula_feedback = (
          r26["final_formula_feedback"]
        + r27["final_formula_feedback"]
        + r28["final_formula_feedback"]
        + r29["final_formula_feedback"]
    )

    final_unit_feedback = (
          r26["final_unit_feedback"]
        + r27["final_unit_feedback"]
        + r28["final_unit_feedback"]
        + r29["final_unit_feedback"]
    )

    temp_feedback = temp["temp_and_celsius_feedback"]

    # ------------------------
    # Return unified V2 structure
    # ------------------------

    return {
        "unit_text_score": unit_text_score,
        "formulas_score": formulas_score,
        "final_formula_score": final_formula_score,
        "final_unit_score": final_unit_score,
        "temp_and_celsius_score": temp_score,

        "unit_text_feedback": unit_text_feedback,
        "formulas_feedback": formulas_feedback,
        "final_formula_feedback": final_formula_feedback,
        "final_unit_feedback": final_unit_feedback,
        "temp_and_celsius_feedback": temp_feedback,
    }
