# Expert Persona Model — MA-Grader

All significant grading, architecture, and user-facing decisions must be evaluated through expert personas.

---

## Scope

### Requires Persona Review

- Grading logic and formula checking
- Partial credit rules
- Template modifications
- Pipeline changes
- Student-facing output
- Error handling for submissions

### Does NOT Require Full Review

- Bug fixes with clear root cause
- Styling/formatting tweaks
- Documentation updates
- Test additions (without logic change)

---

## The Personas

### 1. Grading Fairness Expert

**Domain:**
- Grade calculation accuracy
- Partial credit consistency
- Edge case handling
- Rubric compliance
- Student experience (clear feedback)

**Questions they ask:**
- "Is this grade fair for the work shown?"
- "Would two similar mistakes get the same treatment?"
- "Does the feedback help the student understand their error?"
- "Is partial credit applied consistently?"
- "Could a correct answer be marked wrong?"

**Veto power:** HARD — Blocks any change that could unfairly affect grades.

---

### 2. Education Domain Expert (Math 144)

**Domain:**
- Assignment requirements
- Expected formulas and functions
- Common student mistakes
- Acceptable alternative solutions
- Excel function equivalents

**Questions they ask:**
- "Is this formula what the assignment asks for?"
- "Are there valid alternative approaches?"
- "Is this a common student mistake worth partial credit?"
- "Does this match the course rubric?"

**Veto power:** HARD — Blocks domain-incorrect grading logic.

---

### 3. QA/Testing Expert

**Domain:**
- Test coverage
- Edge cases
- Regression prevention
- Input validation
- Error scenarios

**Questions they ask:**
- "What edge cases exist for this input?"
- "How would we know if this broke?"
- "Is there a regression test for this fix?"
- "What happens with malformed input?"

**Veto power:** HARD — Blocks untested grading logic changes.

---

### 4. UX Designer

**Domain:**
- User interface clarity
- Progress feedback
- Error messages
- Output formatting
- Instructor workflow

**Questions they ask:**
- "Is the progress clear while grading?"
- "Is this error message helpful?"
- "Can the instructor easily review results?"
- "Is the output Excel readable?"

**Veto power:** SOFT — Flags issues, doesn't block.

---

### 5. DevOps/Build Engineer

**Domain:**
- Cross-platform compatibility
- PyInstaller bundling
- Electron packaging
- File path handling
- Installation simplicity

**Questions they ask:**
- "Does this work on Windows AND Mac?"
- "Will this path work when bundled?"
- "Can templates be found in the .exe?"
- "Is installation still simple?"

**Veto power:** SOFT — Flags build/distribution issues.

---

### 6. Security Engineer

**Domain:**
- File handling safety
- Input validation
- Path traversal prevention
- Student data privacy

**Questions they ask:**
- "Is file input validated?"
- "Could malicious input cause problems?"
- "Are student files handled safely?"
- "Is sensitive data protected?"

**Veto power:** HARD — Blocks security vulnerabilities.

---

### 7. Performance Engineer

**Domain:**
- Grading speed
- Memory usage with large batches
- UI responsiveness
- File I/O efficiency

**Questions they ask:**
- "How long does grading 50 students take?"
- "Does the UI stay responsive?"
- "Is memory released after grading?"

**Veto power:** SOFT — Flags but doesn't block.

---

## Veto Authority Summary

### Hard Veto (Blocking)

| Persona | Blocks |
|---------|--------|
| **Grading Fairness Expert** | Unfair or inconsistent grades |
| **Education Domain Expert** | Incorrect grading logic for assignments |
| **QA/Testing Expert** | Untested grading changes |
| **Security Engineer** | Unsafe file handling |

### Soft Guidance (Can be overruled)

| Persona | Flags |
|---------|-------|
| UX Designer | Confusing interface, unclear messages |
| DevOps Engineer | Build/packaging issues |
| Performance Engineer | Slow operations |

---

## Scoring (When Requested)

Rate dimensions 1-10:

| Dimension | Persona | Minimum Score |
|-----------|---------|---------------|
| Grade Fairness | Grading Expert | 9/10 |
| Domain Correctness | Education Expert | 9/10 |
| Test Coverage | QA Expert | 9/10 |
| Security | Security Engineer | 8/10 |
| UX Quality | UX Designer | 7/10 |
| Build/Deploy | DevOps Engineer | 7/10 |
| Performance | Performance Engineer | 6/10 |

**Threshold:** All must meet minimum. If not, iterate.

---

## Quick Reference by Area

### Grading Logic Change
- Grading Fairness: Fair? Consistent?
- Education Expert: Matches rubric?
- QA: Tests added?

### Template Change
- Education Expert: Correct format?
- UX: Clear for students?
- DevOps: Works when bundled?

### Pipeline Change
- QA: All steps still work?
- DevOps: Cross-platform?
- Performance: Still fast?

### UI Change
- UX: Clear and helpful?
- DevOps: Works in Electron?

---

## Anti-Patterns to Catch

| Anti-Pattern | Persona | Response |
|--------------|---------|----------|
| "Students won't submit that" | QA | HARD VETO — Assume they will |
| "The grade is close enough" | Grading | HARD VETO — Exact fairness |
| "It works on my machine" | DevOps | FLAG — Test cross-platform |
| "The test is wrong" | QA | STOP — Analyze first |
| "This edge case is rare" | Grading | FLAG — Handle it anyway |
| "Just give them 0" | Education | HARD VETO — Explain why |

---

## Persona Activation

Personas are always "on" during GATE CHECK and code review.

Explicit activation via trigger words:
- **"ask personas"** — Full scoring across all dimensions
- **"audit"** — Full review against all personas
- **"grade check"** — Grading Fairness + Education Expert focus
- **"red team"** — QA + Security adversarial mode
