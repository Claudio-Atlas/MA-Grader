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

    # Row 6 - Scatterplot Chart & Labels (6 points max)
    grading_ws["F6"] = ia_results.get("scatterplot_chart_score", 0)
    
    # Row 7 - Scatterplot Trendline (2 points max)
    grading_ws["F7"] = ia_results.get("scatterplot_trendline_score", 0)
    
    # Feedback goes in G6 (covers both rows)
    grading_ws["G6"] = render_feedback(ia_results.get("scatterplot_feedback"), TAB)
