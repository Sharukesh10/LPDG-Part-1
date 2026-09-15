# Phase 1.5: Required Submission Documentation

**Status:** PASS  
**Phase:** 1.5 — Submission Documentation  
**Date:** 2026-09-16  

---

## 1. Executive Summary

Phase 1.5 created all human-facing documentation required by the challenge brief. Every quantitative claim is verified against project artifacts. No fake results were generated.

---

## 2. Documentation Deliverables

### DECISIONS.md — CREATED

Five decisions documented with alternatives, evidence, and trade-offs:

| # | Decision |
| :--- | :--- |
| 1 | Reproduce supplied baseline exactly for Part 1 |
| 2 | Treat overlapping windows as modelling limitation, not future-data leakage |
| 3 | Preserve exact duplicate telemetry rather than deduplicate |
| 4 | Preserve supplied tie-breaking behaviour in Part 1 |
| 5 | **Part 2 area: Data Science** |

### LIMITATIONS.md — CREATED

Eight evidence-backed limitations documented:

1. Does not prove a gateway requires a visit
2. Does not optimise €380/€600 operational cost
3. Silent telemetry gaps not in score
4. Rank-cutoff ties ambiguous (7/8 weeks)
5. Reference/detection windows overlap (self-normalisation)
6. Field visits are selection-biased
7. Engineer review temporally limited (2026-02-15 only)
8. Rankings without calibrated uncertainty

**Two-week improvement plan included** — 14 days broken into defensible milestones.

### AI-USAGE.md — CREATED

- Seven categories of AI usage documented
- **Genuine AI mistake documented:** AI initially described overlapping windows as "target leakage"; corrected to "reference-window contamination / self-normalisation" during human review
- Verification methods listed (tests, validator, parity, audit, type-checking, manual review)

### README.md — UPDATED

- What the project does
- Installation and one-command execution
- Project structure
- Verification summary
- Part 2 area stated (Data Science)
- Links to DECISIONS.md, LIMITATIONS.md, AI-USAGE.md

---

## 3. Documentation Consistency Scan

Searched all tracked Markdown files for contradictory claims:

| Search Term | Result |
| :--- | :--- |
| "target leakage" | Not found ✅ |
| "future leakage" | Only legitimate uses (explicitly NOT for windows; correctly applied to engineer review) ✅ |
| "144" | Not found ✅ |
| "0.0" in score-range context | Not found (only in score-delta=0.0 and parity %) ✅ |
| "6 of 8" | Not found ✅ |
| "7 of 8" / "7/8" | Correct usage (rank-15 ties) ✅ |
| Duplicate descriptions | Precise and consistent ✅ |

### BASELINE_REPORT.md Correction

Fixed one remaining stale reference: "In-Sample Target Leakage" → "Reference-Window Overlap (Self-Normalisation)" with corrected explanation.

---

## 4. Git History Verification

```
* cfe8a99 docs: Phase 1.4 — freeze final Part 1 predictions
* 666a041 test: add prediction parity and validation checks
* aaa2fe0 feat: add modular baseline prediction pipeline
* f34a083 test: add gateway data audit and safety checks
* 4d0c387 chore: initialise reproducible challenge environment
```

Five logical, incremental commits representing normal development history. No squashing, no rewriting.

---

## 5. Technical Regression Verification

| Check | Result |
| :--- | :--- |
| `make run` | PASS |
| Official validator | PASS |
| pytest | 33/33 PASS |
| predictions.csv MD5 | `fbd532fe4364809a9cae5c218f0f8841` (unchanged) |

---

## 6. Phase Completion Summary

| Phase | Status |
| :--- | :--- |
| 1.1 — Baseline reproduction | PASS |
| 1.2 — Data audit | PASS |
| 1.2A — Audit/data-safety corrections | PASS |
| 1.3 — Reliable prediction pipeline | PASS |
| 1.4 — Final prediction freeze | PASS |
| **1.5 — Submission documentation** | **PASS** |

---

## 7. Remaining Part 1 Requirements

- [ ] 6–8 minute screen recording showing what was built and one result
- [ ] Final acceptance review
