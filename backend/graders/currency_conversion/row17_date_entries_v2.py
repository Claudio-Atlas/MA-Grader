# graders/currency_conversion_v2/row17_date_entries_v2.py

from datetime import datetime, date


def grade_row17_date_entries_v2(sheet):
    """
    Currency Conversion V2 — Row 17 (C17–F17)

    Rule (same as V1):
      - Each cell must contain a valid date
      - Date must be within 21 days of today's date (absolute difference)

    Scoring:
      - 0.5 points per valid recent date (max 2.0)

    Returns:
      (score: float, feedback: list[(code, params)], parsed_dates: list[date|None])
    """

    today = datetime.today().date()
    max_age_days = 21

    score = 0.0
    feedback = []
    parsed_dates = []

    for col in ["C", "D", "E", "F"]:
        cell = f"{col}17"
        cell_value = sheet[cell].value

        if not cell_value:
            feedback.append(("CC17_DATE_MISSING", {"cell": cell}))
            parsed_dates.append(None)
            continue

        try:
            # If Excel stored a datetime, use it directly
            if isinstance(cell_value, datetime):
                date_val = cell_value.date()
            # Sometimes Excel cells can come through as date objects
            elif isinstance(cell_value, date):
                date_val = cell_value
            else:
                # Accept typed MM/DD/YYYY
                date_val = datetime.strptime(str(cell_value), "%m/%d/%Y").date()

            age_days = abs((today - date_val).days)

            if age_days <= max_age_days:
                score += 0.5
                feedback.append(("CC17_DATE_VALID", {"cell": cell, "date": str(date_val), "age_days": age_days}))
            else:
                feedback.append((
                    "CC17_DATE_TOO_OLD",
                    {"cell": cell, "date": str(date_val), "max_days": max_age_days, "age_days": age_days}
                ))

            parsed_dates.append(date_val)

        except Exception:
            feedback.append(("CC17_DATE_PARSE_ERROR", {"cell": cell}))
            parsed_dates.append(None)

    score_rounded = round(score, 1)
    if score_rounded == 2.0:
        feedback.insert(0, ("CC17_ALL_VALID", {"points": 2.0, "max_days": max_age_days}))
    elif score_rounded > 0:
        feedback.insert(0, ("CC17_PARTIAL", {"earned": score_rounded, "possible": 2.0, "max_days": max_age_days}))
    else:
        feedback.insert(0, ("CC17_NONE_VALID", {"possible": 2.0, "max_days": max_age_days}))

    return score_rounded, feedback, parsed_dates
