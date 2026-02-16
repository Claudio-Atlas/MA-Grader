# DQ Checker - Topic 1 DQ 1

Auto-checks student DQ submissions and generates AI feedback.

## Python Version (Recommended)

No Excel required! Works on any Mac.

### Setup

1. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```
   Or add to `~/.zshrc` for permanent setup.

2. **That's it!** The script uses the MA Grader's Python environment.

### Usage

```bash
cd ~/Desktop/MA-Grader/dq-checker
source ../backend/venv/bin/activate

# Check a file (with AI feedback)
python dq1_checker.py "StudentFile.xlsx"

# Check without AI (just show errors)
python dq1_checker.py "StudentFile.xlsx" --no-ai
```

Output is automatically **copied to clipboard** — just paste into LMS!

### Quick Alias (Optional)

Add to `~/.zshrc`:
```bash
alias dqcheck='cd ~/Desktop/MA-Grader/dq-checker && source ../backend/venv/bin/activate && python dq1_checker.py'
```

Then use:
```bash
dqcheck "StudentFile.xlsx"
```

---

## What It Checks

| Area | Checks |
|------|--------|
| **Inputs (B8, C8)** | Values exist and are numeric |
| **Basic Formulas (F8-F12)** | Uses formulas (not hardcoded), correct operators, references B8/C8 |
| **Basic Formatting** | 2 decimal places on results |
| **Range Data (E20-E27)** | Has numeric data |
| **Range Formulas (H20-H22)** | Uses AVERAGE/SUM/PRODUCT, uses colon range (not commas) |
| **Range Formatting** | H20=2 dec, H21=1 dec, H22=3 dec |

---

## Cost

~$0.0001 per check (one hundredth of a cent)

$5 of API credit = ~50,000 checks

---

## Files

- `dq1_checker.py` - Python script (recommended)
- `Topic1_DQ1_Checker.bas` - VBA macro (requires Excel)

---

## VBA Version (Requires Excel)

See bottom of this file for VBA setup instructions if you have Excel installed.

<details>
<summary>VBA Setup Instructions</summary>

### 1. Get an OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new key
3. Add some credits ($5 is plenty)

### 2. Import the Macro

**Option A: Add to Personal Macro Workbook (recommended)**
1. Open Excel
2. Press `Alt+F11` to open VBA editor
3. In the left panel, find `PERSONAL.XLSB`
4. Right-click → Import File → select `Topic1_DQ1_Checker.bas`
5. Find `OPENAI_API_KEY` at the top and paste your key

**Option B: Add to a specific file**
1. Open the DQ template
2. Press `Alt+F11`
3. Right-click on the workbook → Import File
4. Save as `.xlsm`

### 3. Enable the XML Reference
1. In VBA editor: Tools → References
2. Check "Microsoft XML, v6.0"

### Usage
1. Open student's DQ file
2. Press `Alt+F8`
3. Run `CheckDQ1AndGenerateFeedback`
4. Paste feedback into LMS

</details>
