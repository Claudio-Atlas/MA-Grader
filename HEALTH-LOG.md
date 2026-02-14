# HEALTH-LOG.md — MA-Grader Change Log

*Chronological log of all changes, audits, and fixes.*

---

## 2026-02-14

### Session: System Setup + Full Audit

**Context:** Added CLAUDE.md + PERSONAS.md + HEALTH tracking system, then ran full audit.

#### ✅ Completed

| Time | Task | Details |
|------|------|---------|
| ~16:25 | Created CLAUDE.md | Project-specific rules, gates, triggers |
| ~16:25 | Created PERSONAS.md | 7 expert personas for grading app |
| ~16:25 | Created HEALTH.md | Current status tracking |
| ~16:25 | Created HEALTH-LOG.md | This file |
| ~16:45 | **Full Audit** | All 7 personas reviewed |

#### Audit Results

| Persona | Score | Status |
|---------|-------|--------|
| Grading Fairness | 8/10 | ✅ Pass |
| Education Expert | 8/10 | ✅ Pass |
| QA/Testing | 5/10 | ❌ FAIL |
| Security | 6/10 | ⚠️ Flag |
| UX | 7/10 | ✅ Pass |
| DevOps | 6/10 | ⚠️ Flag |
| Performance | 7/10 | ✅ Pass |

**Overall: C+**

#### Critical Findings

1. **16 failing tests** — Stale references to removed phase2/3/4 modules
2. **ZIP slip vulnerability** — `extractall()` without path validation
3. **Windows build outdated** — PyInstaller fix not rebuilt

#### Files Created

- `CLAUDE.md`
- `PERSONAS.md`
- `HEALTH.md`
- `HEALTH-LOG.md`
- `AUDIT-2026-02-14.md`

---

### Session: P0 #1 Fix — Tests (16:50)

**Context:** Fixing all failing tests identified in audit.

#### ✅ Completed

| Task | Details |
|------|---------|
| Removed stale phase2/3/4 tests | Pipeline simplified, tests referenced removed modules |
| Fixed TestPercentileFormula | Function signature changed, tests not updated |
| Added MA3 tests | Better coverage for MA3 grading |

#### Test Results

- **Before:** 16 failed, 352 passed
- **After:** 0 failed, 362 passed, 11 skipped

#### Commits

| Hash | Message |
|------|---------|
| d1fdcc1 | Fix all failing tests — 362 passing, 0 failing |

#### Score Impact

| Persona | Before | After |
|---------|--------|-------|
| QA/Testing | 5/10 | **8/10** |
| Overall | C+ | **B** |

---

### Session: P1 #3 Fix — ZIP Security (17:05)

**Context:** Fixing ZIP slip vulnerability identified in audit.

#### ✅ Completed

| Task | Details |
|------|---------|
| Added _is_safe_path() | Validates target path is within base directory |
| Added _safe_extract() | Validates all ZIP members before extraction |
| Added security tests | 7 new tests covering path traversal attacks |

#### Security Features

- Blocks `../` path traversal in ZIP entries
- Blocks absolute paths in ZIP entries
- Validates all members BEFORE extracting any
- Raises ValueError with clear message on attack attempt

#### Test Results

- **Before:** 362 passed
- **After:** 369 passed (7 new security tests)

#### Commits

| Hash | Message |
|------|---------|
| 8e3a792 | P1 #3: Fix ZIP slip vulnerability |

#### Score Impact

| Persona | Before | After |
|---------|--------|-------|
| Security | 6/10 | **8/10** |
| Overall | B | **B+** |

---

### Session: P1 #4 — GitHub Actions CI (17:15)

**Context:** Adding automated testing to catch regressions.

#### ✅ Completed

| Task | Details |
|------|---------|
| Created ci.yml workflow | Runs on push to main/develop and all PRs |
| Backend tests job | pytest with coverage reporting |
| Frontend tests job | vitest (continues on error if not set up) |
| Lint check job | flake8 for Python code |
| Security check job | safety for known vulnerabilities |
| Test summary job | Posts summary to GitHub, fails on backend test failure |

#### CI Features

- **Runs on:** Push to main/develop, all PRs
- **Caching:** pip dependencies cached for speed
- **Coverage:** Uploaded to Codecov (optional)
- **Blocking:** Backend test failure blocks merge

#### Commits

| Hash | Message |
|------|---------|
| 35ff102 | P1 #4: Add GitHub Actions CI workflow |

#### Score Impact

| Persona | Before | After |
|---------|--------|-------|
| QA/Testing | 8/10 | **9/10** |
| DevOps | 6/10 | **7/10** |
| Overall | B+ | **A-** |

---

### Session: P2 #8 — Document Formulas (17:25)

**Context:** Document acceptable formula variations for Education Expert.

#### ✅ Completed

| Task | Details |
|------|---------|
| Updated CLAUDE.md | Added formula variation tables |
| Income Analysis | SLOPE, INTERCEPT, predictions patterns |
| Unit Conversions | Temperature, length formulas |
| Currency Conversion | Exchange rate patterns |
| MA3 Analysis | All statistics with variants |

#### Commits

| Hash | Message |
|------|---------|
| 11410dc | P2 #7: Document acceptable formula variations |

#### Score Impact

| Persona | Before | After |
|---------|--------|-------|
| Education Expert | 8/10 | **9/10** |

---

### Session: P2 #7 — Progress Percentage (17:35)

**Context:** Adding visual progress feedback for better UX.

#### ✅ Completed

| Component | Change |
|-----------|--------|
| Backend server.py | Added progress_percent field, set_pipeline_progress() helper |
| Frontend App.jsx | Added ProgressBar component with animated bar |

#### UI Change

```
Before:                      After:
Step 3/6: Grading...         Step 3/6: Grading...
[○][○][●][○][○][○]           Progress: 50%
                             [████████░░░░░░░░]
                             [○][○][●][○][○][○]
```

#### Commits

| Hash | Message |
|------|---------|
| f22fd6f | P2 #7: Add progress percentage display |

#### Score Impact

| Persona | Before | After |
|---------|--------|-------|
| UX Designer | 7/10 | **8/10** |

---

## 2026-02-08

### Session: Pipeline Streamlining

**Context:** Removed unnecessary chart phases, fixed PyInstaller bundling.

#### ✅ Completed

| Task | Details |
|------|---------|
| Pipeline simplified | 8 steps → 6 steps |
| Chart phases removed | Not needed with openpyxl grading |
| PyInstaller fix | Templates/feedback load in .exe |
| Edge case fix | `_detect_assignment_type` handles missing paths |
| Tests | 373 passing (was 372) |

#### Commits

| Hash | Message |
|------|---------|
| 668d4bb | Pipeline streamlining + PyInstaller fix |

---

## 2026-02-07

### Session: Partial Credit System

**Context:** Implemented fair grading for common student mistakes.

#### ✅ Completed

| Task | Details |
|------|---------|
| Partial credit rules | 50% comma/colon, 75% offset |
| MA3 routing | Assignment type properly routed |
| Dynamic naming | `_{assignment_type}_Grade.xlsx` |

---

## Score Progress

| Date | Overall | Grading | Tests | DevOps | Notes |
|------|---------|---------|-------|--------|-------|
| 2026-02-14 | ? | ? | 9/10 | 7/10 | System setup, audit pending |
| 2026-02-08 | — | — | 9/10 | — | 373 tests passing |

---

## Template for Future Entries

```markdown
## YYYY-MM-DD

### Session: [Brief Description]

#### ✅ Completed
| Time | Task | Details |
|------|------|---------|

#### 🔄 In Progress
| Task | Status | Notes |
|------|--------|-------|

#### ⏸️ Blocked
| Task | Blocker | ETA |
|------|---------|-----|

#### Commits
| Hash | Message |
|------|---------|

#### Notes
- [Any important observations]
```
