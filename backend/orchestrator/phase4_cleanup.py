# orchestrator/phase4_cleanup.py

import os
import shutil
from utilities.paths import ws_path


def phase4_cleanup_temp(temp_folder: str = None):
    """
    Deletes the workspace temp_charts folder after chart insertion.

    If temp_folder is provided, it may be an absolute path.
    If not provided, defaults to Documents/MA1_Autograder/temp_charts/
    """
    target = temp_folder or ws_path("temp_charts")

    if os.path.exists(target):
        shutil.rmtree(target)
        print(f"\n[CLEANUP] PHASE 4 — Cleaned up: {target}")
