# HEALTH-LOG.md — MA-Grader Change Log

*Chronological log of all changes, audits, and fixes.*

---

## 2026-02-14

### Session: System Setup

**Context:** Added CLAUDE.md + PERSONAS.md + HEALTH tracking system.

#### ✅ Completed

| Time | Task | Details |
|------|------|---------|
| — | Created CLAUDE.md | Project-specific rules, gates, triggers |
| — | Created PERSONAS.md | 7 expert personas for grading app |
| — | Created HEALTH.md | Current status tracking |
| — | Created HEALTH-LOG.md | This file |

#### Status

- Full audit pending
- Ready for persona review

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
