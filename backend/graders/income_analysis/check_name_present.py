# graders/income_analysis/check_name_present.py

def check_name_present(ws_income):
    """
    Check if a name is present in cell B1 of the Income Analysis worksheet.

    Returns:
        (score: int, feedback: list[tuple[str, dict]])
    """
    name_cell = ws_income["B1"]
    name = str(name_cell.value).strip() if name_cell.value else ""

    if name:
        return 1, [("IA_NAME_PRESENT", {"cell": "B1"})]
    else:
        return 0, [("IA_NAME_MISSING", {"cell": "B1"})]
