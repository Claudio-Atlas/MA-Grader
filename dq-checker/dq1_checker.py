#!/usr/bin/env python3
"""
DQ1 Checker - Topic 1 DQ 1 (Basic Excel Formulas)

Auto-checks student DQ submissions and generates AI feedback.

Usage:
    python dq1_checker.py "StudentFile.xlsx"
    python dq1_checker.py "StudentFile.xlsx" --no-ai   # Skip AI feedback
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from typing import List, Optional

try:
    import openpyxl
except ImportError:
    print("Error: openpyxl not installed. Run: pip install openpyxl")
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None  # Will fail gracefully if AI feedback requested

# ============================================
# CONFIGURATION
# ============================================

# Set your API key here OR use environment variable OPENAI_API_KEY
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = "gpt-4o-mini"

# ============================================
# CHECK FUNCTIONS
# ============================================

def check_input_cells(ws) -> List[str]:
    """Check if inputs B8 and C8 exist and are numeric."""
    errors = []
    
    cell_a = ws['B8'].value
    cell_b = ws['C8'].value
    
    if cell_a is None or cell_a == "":
        errors.append("Cell B8 (input 'a'): No value entered")
    elif not isinstance(cell_a, (int, float)):
        try:
            float(cell_a)
        except (ValueError, TypeError):
            errors.append(f"Cell B8 (input 'a'): Should be a number, found '{cell_a}'")
    
    if cell_b is None or cell_b == "":
        errors.append("Cell C8 (input 'b'): No value entered")
    elif not isinstance(cell_b, (int, float)):
        try:
            float(cell_b)
        except (ValueError, TypeError):
            errors.append(f"Cell C8 (input 'b'): Should be a number, found '{cell_b}'")
    
    return errors


def check_basic_formulas(ws) -> List[str]:
    """Check formulas in F8:F12 for basic operations."""
    errors = []
    
    operations = [
        (8, "addition (a+b)", "+"),
        (9, "subtraction (a-b)", "-"),
        (10, "multiplication (a*b)", "*"),
        (11, "division (a/b)", "/"),
        (12, "exponentiation (a^b)", "^"),
    ]
    
    for row, op_name, operator in operations:
        cell = ws[f'F{row}']
        value = cell.value
        
        if value is None or value == "":
            errors.append(f"Cell F{row} ({op_name}): Empty - needs a formula")
        elif not isinstance(value, str) or not value.startswith('='):
            errors.append(f"Cell F{row} ({op_name}): Hardcoded value '{value}' - should be a formula using cell references")
        else:
            formula = value.upper()
            # Check for correct operator
            if operator not in value:
                errors.append(f"Cell F{row} ({op_name}): Formula '{value}' doesn't appear to use the {operator} operator")
            # Check for B8 and C8 references
            if "B8" not in formula or "C8" not in formula:
                errors.append(f"Cell F{row} ({op_name}): Formula should reference cells B8 and C8 (the input values)")
    
    return errors


def check_basic_formatting(ws) -> List[str]:
    """Check that F8:F12 are formatted to 2 decimal places."""
    errors = []
    
    for row in range(8, 13):
        cell = ws[f'F{row}']
        if cell.value is not None and isinstance(cell.value, (int, float)):
            num_format = cell.number_format or "General"
            # Check for 2 decimal places
            if ".00" not in num_format and num_format == "General":
                errors.append(f"Cell F{row}: Should be formatted to show 2 decimal places")
    
    return errors


def check_range_data(ws) -> List[str]:
    """Check that E20:E27 has numeric data."""
    errors = []
    has_data = False
    
    for row in range(20, 28):
        cell = ws[f'E{row}']
        if cell.value is not None and isinstance(cell.value, (int, float)):
            has_data = True
            break
    
    if not has_data:
        errors.append("Data range E20:E27: No numeric data entered - need values for the range operations")
    
    return errors


def check_range_formulas(ws) -> List[str]:
    """Check formulas in H20:H22 for AVERAGE, SUM, PRODUCT."""
    errors = []
    
    checks = [
        (20, "AVERAGE"),
        (21, "SUM"),
        (22, "PRODUCT"),
    ]
    
    for row, func_name in checks:
        cell = ws[f'H{row}']
        value = cell.value
        
        if value is None or value == "":
            errors.append(f"Cell H{row} ({func_name}): Empty - needs a formula")
        elif not isinstance(value, str) or not value.startswith('='):
            errors.append(f"Cell H{row} ({func_name}): Hardcoded value '{value}' - should be a formula")
        else:
            formula = value.upper()
            # Check for correct function
            if func_name not in formula:
                errors.append(f"Cell H{row}: Should use the {func_name} function")
            # Check for proper range with colon
            if "E20:E27" not in formula.replace("$", "").upper():
                if "," in formula and ":" not in formula:
                    errors.append(f"Cell H{row}: Use a range with colon (E20:E27) instead of listing individual cells with commas")
                elif "E20" not in formula.upper() or "E27" not in formula.upper():
                    errors.append(f"Cell H{row}: Range should be E20:E27 (check your range references)")
    
    return errors


def check_range_formatting(ws) -> List[str]:
    """Check formatting of H20 (2 dec), H21 (1 dec), H22 (3 dec)."""
    errors = []
    
    # H20 = 2 decimals
    cell = ws['H20']
    if cell.value is not None and isinstance(cell.value, (int, float)):
        num_format = cell.number_format or "General"
        if ".00" not in num_format and num_format == "General":
            errors.append("Cell H20 (Average): Should be formatted to 2 decimal places")
    
    # H21 = 1 decimal
    cell = ws['H21']
    if cell.value is not None and isinstance(cell.value, (int, float)):
        num_format = cell.number_format or "General"
        if ".0" not in num_format and num_format == "General":
            errors.append("Cell H21 (Sum): Should be formatted to 1 decimal place")
    
    # H22 = 3 decimals
    cell = ws['H22']
    if cell.value is not None and isinstance(cell.value, (int, float)):
        num_format = cell.number_format or "General"
        if ".000" not in num_format and num_format == "General":
            errors.append("Cell H22 (Product): Should be formatted to 3 decimal places")
    
    return errors


# ============================================
# AI FEEDBACK GENERATION
# ============================================

def generate_ai_feedback(student_name: str, errors: List[str], api_key: str) -> str:
    """Generate feedback using OpenAI API."""
    if not requests:
        return "Error: 'requests' library not installed. Run: pip install requests\n\nErrors found:\n" + "\n".join(f"- {e}" for e in errors)
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return "API key not configured.\n\nErrors found:\n" + "\n".join(f"- {e}" for e in errors)
    
    error_text = "\n".join(f"- {e}" for e in errors)
    
    system_prompt = """You are Professor Clayton Ragsdale, a supportive online math instructor at GCU. 
Write DQ feedback that is warm but direct. Your style:
- Start with 'Hi [FirstName],' (friendly, not formal)
- Be encouraging but clear about exactly what needs fixing
- Give specific cell references and what the correct approach is
- Keep it concise - students skim, so bullet points are good for multiple issues
- End with: let them know if they resubmit with corrections, you can regrade and it will count as a substantive post
- Sign off with just 'Professor Ragsdale' (no email, keep it short)
- Tone: helpful teacher, not robotic grader. You want them to learn.
- Do NOT use emojis in DQ feedback (save those for announcements)
- Keep total response under 150 words unless many errors"""

    user_prompt = f"""Student: {student_name}

Assignment: Topic 1 DQ 1 (Basic Excel Formulas)

Errors found:
{error_text}

Write the feedback response I'll paste into the LMS."""

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": 500,
                "temperature": 0.7,
            },
            timeout=30,
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"API Error ({response.status_code}): {response.text}\n\nErrors found:\n{error_text}"
    
    except Exception as e:
        return f"API Error: {str(e)}\n\nErrors found:\n{error_text}"


# ============================================
# CLIPBOARD
# ============================================

def copy_to_clipboard(text: str):
    """Copy text to clipboard (macOS)."""
    try:
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))
        return True
    except Exception:
        return False


# ============================================
# MAIN
# ============================================

def check_dq1(file_path: str, use_ai: bool = True, api_key: str = "") -> str:
    """
    Check a DQ1 submission file and generate feedback.
    
    Args:
        file_path: Path to the Excel file
        use_ai: Whether to generate AI feedback
        api_key: OpenAI API key (uses env var if not provided)
    
    Returns:
        Feedback string
    """
    # Load workbook
    try:
        wb = openpyxl.load_workbook(file_path)
    except Exception as e:
        return f"Error opening file: {str(e)}"
    
    # Find the worksheet
    sheet_name = "Basic Excel Formulas"
    if sheet_name not in wb.sheetnames:
        # Try to find a similar sheet
        for name in wb.sheetnames:
            if "basic" in name.lower() or "formula" in name.lower():
                sheet_name = name
                break
        else:
            return f"Error: Could not find '{sheet_name}' worksheet. Found: {wb.sheetnames}"
    
    ws = wb[sheet_name]
    
    # Get student name
    student_name = ws['H2'].value
    if not student_name or student_name == "Your Name Here":
        student_name = "Student"
    else:
        student_name = str(student_name).strip()
        # Get first name only
        if " " in student_name:
            student_name = student_name.split()[0]
    
    # Collect all errors
    all_errors = []
    all_errors.extend(check_input_cells(ws))
    all_errors.extend(check_basic_formulas(ws))
    all_errors.extend(check_basic_formatting(ws))
    all_errors.extend(check_range_data(ws))
    all_errors.extend(check_range_formulas(ws))
    all_errors.extend(check_range_formatting(ws))
    
    wb.close()
    
    # No errors?
    if not all_errors:
        return f"✓ No corrections needed for {student_name}! This submission looks good."
    
    # Generate feedback
    if use_ai:
        key = api_key or OPENAI_API_KEY
        feedback = generate_ai_feedback(student_name, all_errors, key)
    else:
        feedback = f"Errors found for {student_name}:\n\n" + "\n".join(f"- {e}" for e in all_errors)
    
    return feedback


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExample:")
        print('  python dq1_checker.py "John_Doe_DQ1.xlsx"')
        print('  python dq1_checker.py "John_Doe_DQ1.xlsx" --no-ai')
        sys.exit(1)
    
    file_path = sys.argv[1]
    use_ai = "--no-ai" not in sys.argv
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"Checking: {file_path}")
    print("-" * 50)
    
    feedback = check_dq1(file_path, use_ai=use_ai)
    print(feedback)
    
    # Copy to clipboard
    if copy_to_clipboard(feedback):
        print("\n" + "-" * 50)
        print("✓ Copied to clipboard - ready to paste!")
    
    return feedback


if __name__ == "__main__":
    main()
