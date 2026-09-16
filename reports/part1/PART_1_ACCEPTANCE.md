# Part 1 — Final Acceptance Review

**Phase:** 1.6 — Final Acceptance Review  
**Date:** 2026-09-16  
**Reviewed against:** LPDG Innovation Hub Selection Challenge 2026 Brief

---

## Requirement Checklist

### Requirement 1 — One-Command Execution
**Status: PASS**

- `make run` executes the pipeline, runs internal validation, writes `predictions.csv`, and passes the official validator. Single command, no manual steps.
- Default data path: `./data`. Alternate path supported: `--data /other/path`.
- `PYTHON ?= python3` in Makefile — no hardcoded interpreter path.
- No hardcoded user-specific paths in `src/`, `scripts/`, `tests/`, or `Makefile`.
- Installation documented in `README.md` (Quick Start section).
- Dependencies in `requirements.txt` and `pyproject.toml`.

---

### Requirement 2 — Valid predictions.csv
**Status: PASS**

| Property | Expected | Verified |
| :--- | :--- | :--- |
| Columns | `week_start, rank, gateway_id, score, reason` | ✅ Exact match |
| Total rows | 120 | ✅ 120 |
| Weeks | 8 (2026-02-02 to 2026-03-23) | ✅ All 8 present |
| Rows per week | 15 | ✅ 15 every week |
| Ranks per week | 1–15, no gaps | ✅ Verified |
| Duplicate gateway per week | 0 | ✅ 0 |
| Score type | Numeric, finite, no missing | ✅ `float64`, range 15–43 |
| Reasons | Non-empty, ≤ 300 chars | ✅ Max 120 chars |
| Official validator | PASS | ✅ `predictions.csv: OK` |
| Baseline parity | 120/120 exact rows | ✅ 100.00% |
| Frozen MD5 | `fbd532fe4364809a9cae5c218f0f8841` | ✅ Unchanged |

---

### Requirement 3 — DECISIONS.md with Five Decisions
**Status: PASS**

Five decisions present. Each includes: chosen approach, alternative considered, and reason for rejection.

| # | Decision |
| :--- | :--- |
| 1 | Reproduce supplied baseline exactly for Part 1 |
| 2 | Treat overlapping windows as modelling limitation, not future-data leakage |
| 3 | Preserve exact duplicate telemetry rather than deduplicate |
| 4 | Preserve supplied tie-breaking behaviour in Part 1 |
| 5 | **Part 2 area: Data Science** |

Decision 5 explicitly states Part 2 = **Data Science** and explains why Machine Learning was not selected.

---

### Requirement 4 — Limitations and Two-Week Plan
**Status: PASS**

`LIMITATIONS.md` contains:

**"What It Cannot Do"** — 8 evidence-backed limitations:

1. Does not prove a gateway requires a visit (score ≠ failure probability)
2. Does not optimise €380/€600 operational cost
3. Silent telemetry gaps not in score
4. Rank-cutoff ties ambiguous (7/8 weeks)
5. Reference/detection windows overlap (self-normalisation)
6. Historical field visits are selection-biased
7. Engineer review temporally limited (2026-02-15 only)
8. Rankings without calibrated uncertainty

**"What Another Two Weeks Would Fix"** — 14-day plan:
- Days 1–3: Define defensible "needs a visit" outcome variable
- Days 4–6: Rolling backtest and €380/€600 cost simulator
- Days 7–9: Test candidate improvements (window, gaps, tie-breakers, thresholds)
- Days 10–11: Uncertainty analysis and hold-out validation
- Days 12–13: Operations-manager charts and failure-case review
- Day 14: Reproducibility and live-change readiness

No unsupported accuracy, precision, recall, ROI, or cost-saving claims present.

---

### Requirement 5 — AI-USAGE.md
**Status: PASS**

- 7 categories of AI tool usage documented.
- Verification methods listed: tests, official validator, parity comparison, data audit, static type-checking, manual review.
- **Genuine AI mistake documented and corrected:**
  - AI described the overlapping reference/detection windows as "target leakage."
  - Human review corrected this: all observations in both windows are strictly before scoring Monday T — no future data is used.
  - Correct term: **reference-window overlap / self-normalisation**.
  - Why it matters: calling it leakage implies a mandatory fix; calling it self-normalisation correctly frames it as a modelling trade-off for Part 2 evaluation.

---

### Requirement 6 — Normal Commit History
**Status: PASS**

7 incremental commits representing logical development progression:

```
00e8f6f  docs: add Part 1 acceptance review and recording plan
dc5a1a8  docs: document Part 1 decisions, limitations, and AI usage
cfe8a99  docs: Phase 1.4 — freeze final Part 1 predictions
666a041  test: add prediction parity and validation checks
aaa2fe0  feat: add modular baseline prediction pipeline
f34a083  test: add gateway data audit and safety checks
4d0c387  chore: initialise reproducible challenge environment
```

- No single giant commit at the end.
- No rewritten or amended history.
- No raw challenge data tracked (`data/` excluded by `.gitignore`).
- No credentials, tokens, or `.env` files.
- No machine-specific hardcoded paths.
- `baseline_3sigma.py` MD5 unchanged from first commit: `a16c349ced7c66a454559ca0ea6423e2`.
- `validate_submission.py` MD5 unchanged from first appearance: `dabf3f44431856366d7bbfac1213d387`.

---

### Requirement 7 — 6–8 Minute Screen Recording
**Status: PENDING HUMAN ACTION**

The recording requires the human candidate to record their screen. See `RECORDING_PLAN.md` for the 7-minute structured plan with segment timings and talking points.

**Selected row for demonstration:**

```
week_start:  2026-02-02
rank:        1
gateway_id:  0A2778A31BE3
score:       43.0
reason:      43 hour(s) beyond 3 sigma of this gateway's own 28-day baseline
             in the last 7 days; first breach on disconnection_cnt
```

Plain-language explanation: This gateway had 43 hours in the last 7 days where its `disconnection_cnt` exceeded its own 28-day historical mean by more than 3 standard deviations. The system is prioritising it for inspection — it is not claiming confirmed failure.

---

## Technical Regression Results

| Check | Result |
| :--- | :--- |
| `make run` | PASS |
| Official validator (`validate_submission.py`) | PASS |
| `pytest` | 33/33 PASS |
| `pyright` | 0 errors, 0 warnings |
| Frozen predictions MD5 | `fbd532fe4364809a9cae5c218f0f8841` ✅ Unchanged |

---

## Repository Safety

| Check | Status |
| :--- | :--- |
| Raw challenge data tracked | No — `data/` excluded by `.gitignore` |
| `.env` / credentials / tokens | None tracked |
| Hardcoded machine-specific paths | None in source |
| Files > 1 MB tracked | None |
| `baseline_3sigma.py` | Unchanged (MD5 verified) |
| `validate_submission.py` | Unchanged (MD5 verified) |

---

## Overall Status

> **PART 1 — TECHNICAL REQUIREMENTS 1–6: PASS**  
> **PART 1 — FULL COMPLETION: PENDING** (Requirement 7 — screen recording requires human action)

Part 1 is not marked complete while the recording is outstanding.
