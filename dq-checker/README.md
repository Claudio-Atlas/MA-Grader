# DQ Checker - Topic 1 DQ 1

Auto-checks student DQ submissions and generates AI feedback.

## Setup (One Time)

### 1. Get an OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new key
3. Add some credits ($5 is plenty — will last thousands of checks)

### 2. Import the Macro

**Option A: Add to Personal Macro Workbook (recommended)**
This lets you use it on ANY DQ file you open.

1. Open Excel
2. Press `Alt+F11` to open VBA editor
3. In the left panel, find `PERSONAL.XLSB` (if it doesn't exist, record a dummy macro first to create it)
4. Right-click → Import File → select `Topic1_DQ1_Checker.bas`
5. Find `OPENAI_API_KEY` at the top and paste your key

**Option B: Add to a specific file**
1. Open the DQ template
2. Press `Alt+F11`
3. Right-click on the workbook → Import File → select `Topic1_DQ1_Checker.bas`
4. Save as `.xlsm` (macro-enabled)

### 3. Enable the XML Reference
1. In VBA editor, go to Tools → References
2. Check "Microsoft XML, v6.0"
3. Click OK

## Usage

### Full Check with AI Feedback
1. Open a student's submitted DQ file
2. Press `Alt+F8`
3. Run `CheckDQ1AndGenerateFeedback`
4. Feedback appears and is copied to clipboard
5. Paste into LMS response

### Quick Test (No API)
Run `TestCheckerNoAPI` to just see the errors without generating AI feedback.

## What It Checks

| Area | Checks |
|------|--------|
| **Inputs (B8, C8)** | Values exist and are numeric |
| **Basic Formulas (F8-F12)** | Uses formulas (not hardcoded), correct operators, references B8/C8 |
| **Basic Formatting** | 2 decimal places on results |
| **Range Data (E20-E27)** | Has numeric data |
| **Range Formulas (H20-H22)** | Uses AVERAGE/SUM/PRODUCT, uses colon range (not commas) |
| **Range Formatting** | H20=2 dec, H21=1 dec, H22=3 dec |

## Cost

~$0.0001 per check (one hundredth of a cent)

$5 of API credit = ~50,000 checks

## Keyboard Shortcut (Optional)

1. In Excel, go to View → Macros → Options
2. Assign a shortcut like `Ctrl+Shift+D`
3. Now checking is instant: open file → `Ctrl+Shift+D` → paste feedback

## Files

- `Topic1_DQ1_Checker.bas` - The VBA module
- `README.md` - This file

## Expanding to Other DQs

Each DQ template will need its own checker module with the specific cells/rules.
The AI feedback generation stays the same — just the detection logic changes.
