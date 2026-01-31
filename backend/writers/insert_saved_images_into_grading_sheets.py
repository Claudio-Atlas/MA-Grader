# writers/insert_saved_images_into_grading_sheets.py
# Cross-platform image insertion (Windows uses COM, macOS uses openpyxl)

import os
import sys
from pathlib import Path

from utilities.paths import ensure_dir

# Check if we're on Windows
IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    try:
        import pythoncom
        import win32com.client as win32
        HAS_WIN32 = True
    except ImportError:
        HAS_WIN32 = False
else:
    HAS_WIN32 = False


def insert_images_into_grading_sheets(temp_chart_dir: str = None, graded_output_dir: str = None):
    """
    Inserts each PNG chart into the corresponding student's grading sheet.
    
    On Windows: Uses Excel COM automation
    On macOS: Uses openpyxl (if images exist)
    """

    if not graded_output_dir:
        raise ValueError("graded_output_dir is required (should be the course folder).")

    # Default to workspace temp_charts
    temp_chart_dir = ensure_dir("temp_charts") if not temp_chart_dir else os.path.abspath(temp_chart_dir)
    graded_output_dir = os.path.abspath(graded_output_dir)

    if not os.path.isdir(temp_chart_dir):
        print(f"[INFO]  No temp_chart_dir found: {temp_chart_dir} (skipping image insertion)")
        return

    pngs = [f for f in os.listdir(temp_chart_dir) if f.lower().endswith(".png")]
    if not pngs:
        print("[INFO]  No PNG charts found to insert (this is normal on macOS).")
        return

    # Use appropriate method based on platform
    if IS_WINDOWS and HAS_WIN32:
        _insert_images_win32(temp_chart_dir, graded_output_dir, pngs)
    else:
        _insert_images_openpyxl(temp_chart_dir, graded_output_dir, pngs)


def _insert_images_openpyxl(temp_chart_dir: str, graded_output_dir: str, pngs: list):
    """Insert images using openpyxl (cross-platform)."""
    try:
        from openpyxl import load_workbook
        from openpyxl.drawing.image import Image
    except ImportError:
        print("[WARN] openpyxl not available for image insertion")
        return

    for image_file in pngs:
        student_name = Path(image_file).stem
        grading_file = os.path.join(graded_output_dir, f"{student_name}_MA1_Grade.xlsx")

        if not os.path.exists(grading_file):
            print(f"[WARN] No grading sheet for {student_name}")
            continue

        image_path = os.path.join(temp_chart_dir, image_file)

        try:
            wb = load_workbook(grading_file)
            ws = wb["Grading Sheet"]

            img = Image(image_path)
            img.anchor = "J4"
            ws.add_image(img)

            wb.save(grading_file)
            print(f"[IMAGE] Inserted chart for {student_name}")

        except Exception as e:
            print(f"[ERROR] Failed to insert chart for {student_name}: {e}")


def _insert_images_win32(temp_chart_dir: str, graded_output_dir: str, pngs: list):
    """Insert images using Windows COM automation."""
    pythoncom.CoInitialize()

    try:
        excel = None

        try:
            excel = win32.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False

            for image_file in pngs:
                student_name = Path(image_file).stem
                grading_file = os.path.join(graded_output_dir, f"{student_name}_MA1_Grade.xlsx")

                if not os.path.exists(grading_file):
                    print(f"[WARN] No grading sheet for {student_name}")
                    continue

                image_path = os.path.join(temp_chart_dir, image_file)

                wb = None
                try:
                    wb = excel.Workbooks.Open(grading_file)
                    ws = wb.Sheets("Grading Sheet")

                    anchor = ws.Range("J4")
                    ws.Shapes.AddPicture(
                        Filename=os.path.abspath(image_path),
                        LinkToFile=False,
                        SaveWithDocument=True,
                        Left=anchor.Left,
                        Top=anchor.Top,
                        Width=-1,
                        Height=-1
                    )

                    wb.Save()
                    wb.Close()
                    wb = None
                    print(f"[IMAGE] Inserted chart for {student_name}")

                except Exception as e:
                    print(f"[ERROR] Failed to insert chart for {student_name}: {e}")
                    try:
                        if wb is not None:
                            wb.Close(SaveChanges=False)
                    except Exception:
                        pass

        finally:
            try:
                if excel is not None:
                    excel.Quit()
            except Exception:
                pass

    finally:
        pythoncom.CoUninitialize()
