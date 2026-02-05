"""
phase4_cleanup.py — Phase 4: Clean up temporary files

Purpose: Removes the temp_charts folder after chart images have been inserted
         into grading sheets. This keeps the workspace clean and reduces
         disk usage, especially when grading multiple courses.

Author: Clayton Ragsdale
Dependencies: utilities.paths
"""

import os
import shutil
from typing import Optional

from utilities.paths import ws_path


def phase4_cleanup_temp(temp_folder: Optional[str] = None) -> None:
    """
    Delete the temporary charts folder after chart insertion is complete.
    
    This cleanup phase runs after Phase 3 (insert charts) to remove the
    PNG files that were created during Phase 2 (export charts). The chart
    images are no longer needed because they've been embedded into the
    grading sheets.
    
    Args:
        temp_folder: Optional absolute path to the temp folder to delete.
                     If not provided, defaults to the workspace temp_charts
                     folder (Documents/MA1_Autograder/temp_charts/).
    
    Behavior:
        - If the folder exists, it is completely removed (including all contents)
        - If the folder doesn't exist, this function does nothing silently
        - Uses shutil.rmtree for recursive deletion
    
    Example:
        >>> phase4_cleanup_temp()
        [CLEANUP] PHASE 4 - Cleaned up: /Users/.../MA1_Autograder/temp_charts
        
        >>> phase4_cleanup_temp("/custom/temp/folder")
        [CLEANUP] PHASE 4 - Cleaned up: /custom/temp/folder
    """
    # Use provided path or default to workspace temp_charts
    target = temp_folder or ws_path("temp_charts")

    # Only attempt deletion if folder exists
    if os.path.exists(target):
        # Recursively delete the entire folder and its contents
        shutil.rmtree(target)
        print(f"\n[CLEANUP] PHASE 4 - Cleaned up: {target}")
