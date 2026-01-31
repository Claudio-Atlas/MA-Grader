# writers/write_income_analysis_scores.py

from utilities.feedback_renderer import render_feedback


def write_income_analysis_scores(grading_ws, ia_results):
    """
    Write Income Analysis scores and feedback to the Grading Sheet.

    Income Analysis now uses feedback codes + params rendered via:
      utilities/feedback_renderer.py + feedback/income_analysis.json
    """
    TAB = "income_analysis"

    # Row 3 - Name
    grading_ws["F3"] = ia_results.get("name_score", 0)
    grading_ws["G3"] = render_feedback(ia_results.get("name_feedback"), TAB)

    # Row 4 - Slope & Intercept (formulas + formatting)
    grading_ws["F4"] = ia_results.get("slope_score", 0)
    grading_ws["G4"] = render_feedback(ia_results.get("slope_feedback"), TAB)

    # Row 5 - Predictions (formulas + formatting)
    grading_ws["F5"] = ia_results.get("predictions_score", 0)
    grading_ws["G5"] = render_feedback(ia_results.get("predictions_feedback"), TAB)

    # Row 6 - Scatterplot (manual)
    # If you still don’t write row 6, keep these commented.
    # grading_ws["F6"] = ia_results.get("scatterplot_score", 0)
    # grading_ws["G6"] = render_feedback(ia_results.get("scatterplot_feedback"), TAB)
