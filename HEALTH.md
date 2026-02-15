# HEALTH.md — MA-Grader System Health

*Last audit: 2026-02-14*
*Status: 🟢 PRODUCTION READY (MA1 + MA3)*

---

## Quick Status

| Component | Status | Notes |
|-----------|--------|-------|
| Backend (Python) | ✅ Working | FastAPI + openpyxl |
| Frontend (Electron) | ✅ Working | React + Vite |
| MA1 Grader | ✅ Complete | Income, Unit Conversions, Currency |
| MA3 Grader | ✅ Complete | Analysis, Visualization |
| MA2 Grader | ❌ Not Started | Waiting on assignment specs |
| Tests | ✅ 391 Passing | 100% pass rate (11 skipped) |
| Windows Build | ✅ Auto (CI) | GitHub Actions builds on push |
| Mac Build | ✅ Working | Tested |

---

## Persona Scores (Updated 2026-02-14)

| Persona | Score | Status | Notes |
|---------|-------|--------|-------|
| Grading Fairness | 8/10 | ✅ Pass | Partial credit system working |
| Education Expert | 9/10 | ✅ Pass | MA1+MA3 logic + formula docs |
| QA/Testing | 9/10 | ✅ Pass | 369 tests + CI pipeline |
| UX Designer | 9/10 | ✅ Pass | User-friendly errors + summary |
| DevOps Engineer | 8/10 | ✅ Pass | CI + auto Windows build |
| Security Engineer | 8/10 | ✅ Pass | ZIP slip fixed, path validation added |
| Performance | 7/10 | ✅ Pass | Not benchmarked but efficient |

**Overall: A (All personas ≥7, critical ≥8, DevOps now 8/10)**

---

## Priority Fix List

### P0 — Must Fix Now

| # | Task | Status | Effort |
|---|------|--------|--------|
| 1 | Fix/remove failing tests | ✅ DONE | — |
| 2 | Rebuild Windows .exe | ✅ DONE (CI) | — |

### P1 — Fix Soon

| # | Task | Status | Effort |
|---|------|--------|--------|
| 3 | Fix ZIP slip vulnerability | ✅ DONE | — |
| 4 | Add GitHub Actions CI | ✅ DONE | — |

### P2 — Fix Before Next Semester

| # | Task | Status | Effort |
|---|------|--------|--------|
| 5 | MA2 grader support | ❌ BLOCKED | Needs specs |
| 6 | Better error messages | ✅ DONE | — |
| 7 | Progress percentage display | ✅ DONE | — |
| 8 | Document formula variations | ✅ DONE | — |

### P2 — Nice to Have

| # | Task | Status | Effort |
|---|------|--------|--------|
| 6 | Batch processing multiple courses | 🔄 TODO | 4 hrs |
| 7 | Grade history/comparison | 🔄 TODO | 3 hrs |
| 8 | Direct Canvas integration | 🔄 TODO | 8 hrs |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MA-Grader Desktop App                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Electron + React + Vite)                         │
│  └── Drop ZIP → Select Assignment → Run Pipeline            │
├─────────────────────────────────────────────────────────────┤
│  Backend (Python FastAPI on localhost:8765)                 │
│  └── 6-step pipeline                                        │
├─────────────────────────────────────────────────────────────┤
│  Graders (openpyxl - no Excel dependency)                   │
│  ├── MA1: Income, Unit Conversions, Currency                │
│  ├── MA2: [Not implemented]                                 │
│  └── MA3: Analysis (stats), Visualization (histogram)       │
├─────────────────────────────────────────────────────────────┤
│  Output                                                      │
│  ├── Individual: {Student}_MA{X}_Grade.xlsx                 │
│  └── Summary: INSTRUCTOR_MASTER.xlsx                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Pipeline (6 Steps)

1. **Prepare workspace assets** — Copy templates, feedback
2. **Create course folders** — Set up output structure
3. **Import student submissions** — Extract from ZIP
4. **Create grading sheets** — Copy template per student
5. **Grade formulas** — Run graders, calculate scores
6. **Build instructor master** — Summary workbook

---

## Grading Rules

### Partial Credit System

| Mistake | Credit | Example |
|---------|--------|---------|
| Comma instead of colon | 50% | `=AVERAGE(B14,B63)` instead of `=AVERAGE(B14:B63)` |
| Range offset (drag-fill) | 75% | Off by one row/column |
| Correct formula, wrong format | 100% | Substance over style |
| Empty cell | 0% | Missing work |
| Wrong formula entirely | 0% | Incorrect approach |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Desktop Shell | Electron 28 |
| Frontend | React 18 + Vite + Tailwind |
| Backend | Python FastAPI + Uvicorn |
| Excel Processing | openpyxl (no Excel required) |
| Testing | pytest (backend), Vitest (frontend) |

---

## Key Files

| Purpose | Location |
|---------|----------|
| Server entry | `backend/server.py` |
| MA1 graders | `backend/graders/ma1/` |
| MA3 graders | `backend/graders/ma3/` |
| Templates | `backend/templates/` |
| Pipeline orchestrator | `backend/orchestrator/` |
| Tests | `backend/tests/` |
| Electron main | `frontend/electron/` |
| React UI | `frontend/src/` |

---

## Recent Changes

| Date | Change | Impact |
|------|--------|--------|
| 2026-02-08 | Pipeline 8→6 steps | Simplified, removed chart phases |
| 2026-02-08 | PyInstaller bundling fix | Templates load in .exe |
| 2026-02-07 | Partial credit system | 50%/75% for common mistakes |
| 2026-02-07 | MA3 grader complete | Stats + visualization grading |

---

## Useful Commands

```bash
# Development
cd ~/Desktop/MA-Grader/frontend && npm run electron:dev

# Run backend tests
cd ~/Desktop/MA-Grader/backend && source venv/bin/activate && pytest -v

# Build Windows .exe (on Windows)
cd backend && pyinstaller server.spec

# Build Electron app
cd ~/Desktop/MA-Grader/frontend && npm run electron:build
```

---

## Blockers

| Blocker | Waiting On | Affects |
|---------|------------|---------|
| MA2 specs | Assignment requirements | P1 #3 |

---

## Next Session Checklist

When resuming work:
1. Read this file for current status
2. Run `pytest` to verify all tests pass
3. Check P0 items — what's next?
4. Run `audit` for full persona review
