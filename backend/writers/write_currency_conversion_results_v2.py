# writers/write_currency_conversion_results_v2.py

from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font
from utilities.feedback_renderer import render_feedback

# Standard black font for feedback cells
BLACK_FONT = Font(color="000000")


def write_currency_conversion_results_v2(ws_grading: Worksheet, results: dict) -> Worksheet:
    """
    Writes Currency Conversion V2 results into the grading sheet.

    Uses:
      feedback/currency_conversion.json
    via:
      utilities/json_loader.py + utilities/feedback_renderer.py
    """

    TAB = "currency_conversion"

    # Row 15
    ws_grading["F15"].value = results.get("row15_score", 0)
    ws_grading["G15"].value = render_feedback(results.get("row15_feedback"), TAB)
    ws_grading["G15"].font = BLACK_FONT

    # Row 16
    ws_grading["F16"].value = results.get("row16_score", 0)
    ws_grading["G16"].value = render_feedback(results.get("row16_feedback"), TAB)
    ws_grading["G16"].font = BLACK_FONT

    # Row 17
    ws_grading["F17"].value = results.get("row17_score", 0)
    ws_grading["G17"].value = render_feedback(results.get("row17_feedback"), TAB)
    ws_grading["G17"].font = BLACK_FONT

    # Row 18
    ws_grading["F18"].value = results.get("row18_score", 0)
    ws_grading["G18"].value = render_feedback(results.get("row18_feedback"), TAB)
    ws_grading["G18"].font = BLACK_FONT

    # Row 19
    ws_grading["F19"].value = results.get("row19_accuracy_score", 0)
    ws_grading["G19"].value = render_feedback(results.get("row19_feedback"), TAB)
    ws_grading["G19"].font = BLACK_FONT

    # Row 20
    ws_grading["F20"].value = results.get("row20_formula_score", 0)
    ws_grading["G20"].value = render_feedback(results.get("row20_feedback"), TAB)
    ws_grading["G20"].font = BLACK_FONT

    # Row 21
    ws_grading["F21"].value = results.get("row21_formula_score", 0)
    ws_grading["G21"].value = render_feedback(results.get("row21_feedback"), TAB)
    ws_grading["G21"].font = BLACK_FONT

    # Formatting Total (final row)
    ws_grading["F22"].value = results.get("formatting_total", 0)

    return ws_grading
