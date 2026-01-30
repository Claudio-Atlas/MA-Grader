# graders/currency_conversion_v2/grade_currency_conversion_tab_v2.py

from .row15_name_letters_v2 import grade_row15_name_letters_v2
from .row16_country_selection_v2 import grade_row16_country_selection_v2
from .row17_date_entries_v2 import grade_row17_date_entries_v2
from .row18_currency_codes_v2 import grade_row18_currency_codes_v2
from .row19_exchange_rates_v2 import grade_row19_exchange_rates_v2, fetch_live_usd_rates
from .row20_budget_conversion_v2 import grade_row20_budget_conversion_v2
from .row21_usd_conversion_back_v2 import grade_row21_usd_conversion_back_v2


def grade_currency_conversion_tab_v2(sheet, student_name: str):
    """
    Currency Conversion V2 wrapper.

    Matches the V1 wrapper's scoring categories and keys, but uses V2 graders
    that return feedback as (code, params).

    Returns:
      dict with:
        row15_score, row15_feedback
        row16_score, row16_feedback
        row17_score, row17_feedback
        row18_score, row18_feedback
        row19_accuracy_score, row19_format_score, row19_feedback
        row20_formula_score, row20_format_score, row20_feedback
        row21_formula_score, row21_format_score, row21_feedback
        formatting_total
    """

    results = {}

    # -----------------------------
    # Row 15
    # -----------------------------
    score15, fb15 = grade_row15_name_letters_v2(sheet, student_name)
    results["row15_score"] = score15
    results["row15_feedback"] = fb15

    # -----------------------------
    # Row 16 (returns entries used by row 18)
    # -----------------------------
    score16, fb16, country_entries = grade_row16_country_selection_v2(sheet, student_name)
    results["row16_score"] = score16
    results["row16_feedback"] = fb16

    # -----------------------------
    # Row 17
    # -----------------------------
    score17, fb17, _parsed_dates = grade_row17_date_entries_v2(sheet)
    results["row17_score"] = score17
    results["row17_feedback"] = fb17

    # -----------------------------
    # Row 18
    # -----------------------------
    score18, fb18 = grade_row18_currency_codes_v2(sheet, country_entries)
    results["row18_score"] = score18
    results["row18_feedback"] = fb18

    # -----------------------------
    # Row 19 (API-based)
    # Fetch once and pass in (future-proof + faster)
    # -----------------------------
    live_rates, err = fetch_live_usd_rates()
    if err:
        score19_total, acc19, fmt19 = 0.0, 0.0, 0.0
        fb19 = [("CC19_API_FETCH_FAILED", {"error": err})]
    else:
        score19_total, acc19, fmt19, fb19 = grade_row19_exchange_rates_v2(sheet, live_rates=live_rates)

    # Wrapper-compatible split (same style as V1)
    results["row19_accuracy_score"] = round(min(acc19, 4.0), 2)
    results["row19_format_score"] = round(max(0.0, fmt19), 2)
    results["row19_feedback"] = fb19

    # -----------------------------
    # Row 20
    # -----------------------------
    score20_total, formula20, fmt20, fb20 = grade_row20_budget_conversion_v2(sheet)
    results["row20_formula_score"] = round(min(formula20, 8.0), 2)
    results["row20_format_score"] = round(max(0.0, fmt20), 2)
    results["row20_feedback"] = fb20

    # -----------------------------
    # Row 21
    # -----------------------------
    score21_total, formula21, fmt21, fb21 = grade_row21_usd_conversion_back_v2(sheet)
    results["row21_formula_score"] = round(min(formula21, 8.0), 2)
    results["row21_format_score"] = round(max(0.0, fmt21), 2)
    results["row21_feedback"] = fb21

    # -----------------------------
    # Formatting Final Total (same as V1)
    # formatting_total = formatting_19 + formatting20 + formatting21 + 1.0
    # max = 4
    # -----------------------------
    raw_formatting_sum = float(results["row19_format_score"]) + float(results["row20_format_score"]) + float(results["row21_format_score"])
    formatting_bonus = 1.0
    formatting_total = round(raw_formatting_sum + formatting_bonus, 2)
    results["formatting_total"] = formatting_total

    return results
