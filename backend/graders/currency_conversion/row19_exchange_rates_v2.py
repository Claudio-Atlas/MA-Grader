# graders/currency_conversion_v2/row19_exchange_rates_v2.py

import requests


def fetch_live_usd_rates():
    """
    Fetch live FX rates with USD as the base currency.
    Returns: (rates_dict, error_message_or_none)
    """
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=15)
        response.raise_for_status()
        rates = response.json().get("rates", {})
        if not isinstance(rates, dict) or not rates:
            return {}, "API returned no rates."
        return rates, None
    except Exception as e:
        return {}, str(e)


def grade_row19_exchange_rates_v2(sheet, live_rates=None):
    """
    Currency Conversion V2 — Row 19 (C19–F19)

    Uses the currency codes in C18–F18 to validate the exchange rates in C19–F19.

    Scoring (same as V1 actual code behavior):
      - Accuracy: within ±5% of live rate → 1.0 pt each (max 4.0)
      - Formatting: must show 3 decimals → 0.25 pt each (max 1.0)

    Returns:
      (total_score, accuracy_score, format_score, feedback)
        feedback is list[(code, params)]
    """

    # Allow reuse of fetched rates (so later wrapper can fetch once)
    if live_rates is None:
        live_rates, err = fetch_live_usd_rates()
        if err:
            return 0.0, 0.0, 0.0, [("CC19_API_FETCH_FAILED", {"error": err})]

    feedback = []

    accuracy_score = 0.0
    format_score = 0.0

    code_cells = ["C18", "D18", "E18", "F18"]
    rate_cells = ["C19", "D19", "E19", "F19"]

    for code_cell, rate_cell in zip(code_cells, rate_cells):
        raw_code = sheet[code_cell].value
        raw_rate = sheet[rate_cell].value

        student_code = str(raw_code).strip().upper() if raw_code else ""
        student_rate = raw_rate if isinstance(raw_rate, (int, float)) else None

        # --- Validate currency code ---
        if not student_code:
            feedback.append(("CC19_CODE_MISSING", {"code_cell": code_cell, "rate_cell": rate_cell}))
        elif student_code not in live_rates:
            feedback.append(("CC19_CODE_INVALID", {"code_cell": code_cell, "code": student_code}))
        else:
            true_rate = live_rates[student_code]
            lower = true_rate * 0.95
            upper = true_rate * 1.05

            if student_rate is None:
                feedback.append(("CC19_RATE_NOT_NUMERIC", {"rate_cell": rate_cell}))
            else:
                if lower <= float(student_rate) <= upper:
                    accuracy_score += 1.0
                    feedback.append((
                        "CC19_RATE_WITHIN_TOLERANCE",
                        {
                            "rate_cell": rate_cell,
                            "student_rate": float(student_rate),
                            "true_rate": float(true_rate),
                            "tolerance": "±5%"
                        }
                    ))
                else:
                    feedback.append((
                        "CC19_RATE_OUTSIDE_TOLERANCE",
                        {
                            "rate_cell": rate_cell,
                            "student_rate": float(student_rate),
                            "true_rate": float(true_rate),
                            "tolerance": "±5%"
                        }
                    ))

        # --- Formatting check (3 decimals) ---
        number_format = sheet[rate_cell].number_format
        fmt = str(number_format) if number_format is not None else ""
        fmt_norm = fmt.replace('"', "").lower()

        if ("0.000" in fmt_norm) or ("#.000" in fmt_norm):
            format_score += 0.25
            feedback.append(("CC19_FORMAT_OK", {"rate_cell": rate_cell}))
        else:
            feedback.append(("CC19_FORMAT_BAD", {"rate_cell": rate_cell}))

    total_score = round(accuracy_score + format_score, 2)

    # Summary line (still code-based)
    feedback.insert(0, (
        "CC19_SUMMARY",
        {
            "accuracy": round(accuracy_score, 2),
            "accuracy_possible": 4.0,
            "formatting": round(format_score, 2),
            "formatting_possible": 1.0,
            "total": total_score,
            "total_possible": 5.0
        }
    ))

    return total_score, round(accuracy_score, 2), round(format_score, 2), feedback
