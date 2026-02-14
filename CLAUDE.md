# CLAUDE.md — MA-Grader

## ⛔ GATE CHECK — Complete Before Every Code Edit

**Do not write or modify code until you've completed this:**

```
GATE CHECK:
- Branch: [current branch, or "creating <type>/<desc>"]
- Student data involved: [yes/no — does this touch student files/grades?]
- Template change: [yes/no — does this modify grading templates?]
- Grading logic change: [yes/no — does this affect how grades are calculated?]
- Tests needed: [which test files, or "none — no logic change"]
- Impact areas: [list from Change Impact Checklist]
```

**Skip gate only for:** answering questions, reading files, running non-edit commands.

---

## ⛔ GRADING GATE — Before ANY Grade Calculation Changes

**Mandatory for anything affecting student grades:**

```
GRADING GATE:
- Formula correct: [verified against assignment rubric]
- Partial credit: [how are edge cases handled?]
- Edge cases: [empty cells? wrong format? extra spaces?]
- Backwards compatible: [will old submissions still grade correctly?]
- Test coverage: [do tests cover this grading scenario?]
```

**Never skip this gate for grading logic. Never.**

---

## ⛔ POST-TEST GATE — After Running Tests

### If tests PASS:
1. Verify grading logic is correct (not just passing)
2. Check edge cases are covered
3. Only then mark complete

### If tests FAIL:
```
TEST FAILURE ANALYSIS:
- Failed test: [name]
- Expected: [what test expected]
- Actual: [what happened]
- Root cause: [implementation bug / test bug / needs investigation]
- Proposed action: [fix implementation / request approval to modify test]
```

**Default assumption: Test failures are implementation bugs, not test bugs.**

---

## Before Writing New Code — STOP

### 1. Search First

```bash
# Check for existing patterns
grep -r "pattern" backend/
grep -r "function" backend/graders/
```

### 2. Know the Grading Rules

| Situation | Rule |
|-----------|------|
| Comma instead of colon in range | 50% partial credit |
| Range offset (drag-fill error) | 75% partial credit |
| Empty cell where formula expected | 0% — missing work |
| Correct formula, wrong format | Full credit (substance over style) |
| Extra whitespace | Strip and compare |

### 3. Code Standards

- **openpyxl only** — No Excel COM automation
- **No hardcoded paths** — Use constants/config
- **Descriptive names** — `calculate_income_total` not `calc`
- **Type hints** — All function signatures
- **Docstrings** — All public functions

---

## Hard Rules — Never Break

### Architecture
- ✅ openpyxl for ALL Excel operations
- ✅ Templates live in `templates/` folder
- ✅ Output goes to `output/` folder
- ✅ Each student gets a copy of grading template
- ❌ Never require Excel installation
- ❌ Never modify student's original file
- ❌ Never hardcode file paths

### Grading
- ✅ Partial credit for common mistakes (see rules above)
- ✅ Case-insensitive formula comparison
- ✅ Trim whitespace before comparing
- ✅ Log all grading decisions
- ❌ Never give 0 without clear reason
- ❌ Never change grading logic without tests
- ❌ Never skip edge case handling

### Testing
- ✅ Test failures = implementation bugs (default)
- ✅ Cover edge cases: empty, malformed, extra spaces
- ✅ Test partial credit scenarios
- ❌ Never modify tests to make them pass without analysis
- ❌ Never skip tests for "simple" changes

---

## Trigger Words

| Word | Action |
|------|--------|
| **"deploy"** | Run full test suite, build for distribution |
| **"audit"** | Full review against PERSONAS |
| **"red team"** | Test with malformed/adversarial input |
| **"spiral"** | Identify drift, correct course |
| **"ask personas"** | Score change against all personas |
| **"gate"** | Re-read this file, state 3 relevant rules |
| **"grade check"** | Full GRADING GATE analysis |

---

## Red Team Protocol

**Triggered by "red team" or for input-handling code.**

### Ask These Questions:

1. **Malformed Input**
   - What if the ZIP is corrupted?
   - What if Excel file is password-protected?
   - What if student used different file format?

2. **Edge Cases**
   - What if cell is empty?
   - What if formula has extra spaces?
   - What if student used different locale (comma vs period)?

3. **Grading Fairness**
   - Could this unfairly penalize a correct answer?
   - Could this give credit for wrong answer?
   - Are partial credit rules applied consistently?

### Output Format:

```
RED TEAM REPORT:
- Issue: [what could go wrong]
- Scenario: [how a student might trigger it]
- Impact: [unfair grade / crash / wrong output]
- Mitigation: [specific fix]

Status: [VULNERABLE / SECURE]
```

---

## Change Impact Checklist

### Backend (`backend/`)

| Area | File(s) |
|------|---------|
| Pipeline | `server.py`, `orchestrator/` |
| Graders | `graders/ma1/`, `graders/ma3/` |
| Templates | `templates/` (Excel files) |
| Writers | `writers/` |
| Utilities | `utilities/` |
| Tests | `tests/` |

### Frontend (`frontend/`)

| Area | File(s) |
|------|---------|
| UI Components | `src/components/` |
| Electron | `electron/` |
| Config | `vite.config.ts`, `tailwind.config.js` |

---

## Ship Checklist

When I say **"deploy"**:

### Tests
1. `pytest` — All 373+ tests must pass
2. `npm run test` — All component tests pass

### Build
3. `pyinstaller server.spec` — Backend builds
4. `npm run electron:build` — Electron builds

### Verify
5. Test with sample ZIP on Mac
6. Test with sample ZIP on Windows
7. Check output files open correctly

---

## AI Behavior

- **Ask before guessing** — If unclear, clarify first
- **Gate before coding** — Always complete GATE CHECK
- **Search before writing** — Check if it exists
- **Minimal changes** — No drive-by refactoring
- **Small patches** — No full-file rewrites
- **Never "fix" tests** — Fix implementation or ask first
- **Grade check always** — Any grading change needs GRADING GATE

---

## Project Context

### What This Is
Desktop app that auto-grades Excel assignments for Math 144. Students submit ZIP files, app processes them through a 6-step pipeline, outputs graded Excel files with scores and feedback.

### Key Architecture
```
Electron Shell → React UI → Python FastAPI → openpyxl Graders → Output
```

### Key Files
- **Server entry:** `backend/server.py`
- **Graders:** `backend/graders/ma1/`, `backend/graders/ma3/`
- **Templates:** `backend/templates/`
- **Pipeline:** `backend/orchestrator/`

---

## Debugging

```bash
# Run backend standalone
cd ~/Desktop/MA-Grader/backend
source venv/bin/activate
python server.py

# Run tests
pytest -v

# Run specific test
pytest tests/test_graders.py -k "test_income"

# Run frontend dev
cd ~/Desktop/MA-Grader/frontend
npm run electron:dev
```
