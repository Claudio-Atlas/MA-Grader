# graders/income_analysis/grade_income_analysis.py

from .check_name_present import check_name_present
from .check_slope_intercept import check_slope_intercept
from .check_slope_intercept_formatting import check_slope_intercept_formatting
from .check_predictions import check_predictions
from .check_predictions_formatting import check_currency_formatting


def grade_income_analysis(ws):
    """
    Run all grading checks for the Income Analysis tab and return a dictionary
    of scores and feedback (feedback is codes+params for JSON rendering).
    """
    results = {}

    # Row 3: Name
    score, fb = check_name_present(ws)
    results["name_score"] = score
    results["name_feedback"] = fb

    # Row 4: Slope/Intercept formulas + formatting
    slope_score, slope_fb = check_slope_intercept(ws)
    fmt_score, fmt_fb = check_slope_intercept_formatting(ws)

    results["slope_score"] = slope_score + fmt_score
    results["slope_feedback"] = (slope_fb or []) + (fmt_fb or [])

    # Row 5: Predictions + formatting
    pred_score, pred_fb = check_predictions(ws)
    pred_fmt_score, pred_fmt_fb = check_currency_formatting(ws)

    results["predictions_score"] = pred_score + pred_fmt_score
    results["predictions_feedback"] = (pred_fb or []) + (pred_fmt_fb or [])

    # Row 6: Scatterplot (manual)
    results["scatterplot_score"] = 0
    results["scatterplot_feedback"] = [("IA_SCATTER_NOT_CHECKED", {})]

    return results
