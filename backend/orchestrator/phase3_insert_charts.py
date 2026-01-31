# orchestrator/phase3_insert_charts.py

from utilities.paths import ensure_dir


def phase3_insert_all_charts(graded_output_path: str):
    """
    Inserts previously exported charts into final grading sheets.
    Only inserts into THIS COURSE folder.
    """
    from writers.insert_saved_images_into_grading_sheets import insert_images_into_grading_sheets

    print("\n[IMPORT] PHASE 3 — Inserting charts into grading sheets...\n")

    temp_dir = ensure_dir("temp_charts")

    insert_images_into_grading_sheets(
        temp_chart_dir=temp_dir,
        graded_output_dir=graded_output_path
    )
