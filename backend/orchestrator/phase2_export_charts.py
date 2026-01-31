# orchestrator/phase2_export_charts.py

import os
from utilities.paths import ensure_dir
from writers.export_chart_to_image import export_chart_to_image


def phase2_export_all_charts(submissions_path: str):
    """
    Exports scatterplot charts for every student submission.
    Safe per-student: one failure won't stop the entire pipeline.

    Exports into workspace: Documents/MA1_Autograder/temp_charts/
    """
    print("\n[CHART] PHASE 2 — Exporting scatterplot charts...\n")

    temp_dir = ensure_dir("temp_charts")

    for filename in os.listdir(submissions_path):
        if not filename.endswith(".xlsx"):
            continue

        full_path = os.path.join(submissions_path, filename)

        try:
            export_chart_to_image(full_path, image_output_dir=temp_dir)
        except Exception as e:
            print(f"[WARN] Chart export failed for {filename}: {e}")
