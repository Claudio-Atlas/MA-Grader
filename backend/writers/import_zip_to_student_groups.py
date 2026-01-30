# writers/import_zip_to_student_groups.py

import os
import shutil
import zipfile
from pathlib import Path

from utilities.paths import ensure_dir


def import_zip_to_student_groups(zip_path: str, course_label: str) -> str:
    """
    Extracts a downloaded student ZIP into workspace:

        Documents/MA1_Autograder/student_groups/<course_label>/

    Returns:
        destination folder path
    """
    zip_path = os.path.abspath(zip_path)
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Zip not found: {zip_path}")
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Not a valid zip file: {zip_path}")

    course_label = (course_label or "").strip()
    if not course_label:
        raise ValueError("Course label cannot be blank.")

    # ✅ Workspace destination
    dest_root = ensure_dir("student_groups", course_label)

    # Extract to a temporary folder first
    temp_extract = os.path.join(dest_root, "_tmp_extract")
    if os.path.exists(temp_extract):
        shutil.rmtree(temp_extract)
    os.makedirs(temp_extract, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(temp_extract)

    # If the zip contains one top-level folder, move its contents up
    items = [p for p in Path(temp_extract).iterdir()]

    if len(items) == 1 and items[0].is_dir():
        top = items[0]
        for child in top.iterdir():
            target = Path(dest_root) / child.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(child), str(target))
    else:
        for child in items:
            target = Path(dest_root) / child.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(child), str(target))

    shutil.rmtree(temp_extract, ignore_errors=True)

    return dest_root
