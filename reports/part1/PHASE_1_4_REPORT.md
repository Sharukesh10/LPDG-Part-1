# Phase 1.4: Freeze Final Part-1 Predictions

**Status:** PASS  
**Phase:** 1.4 — Final Prediction Freeze  
**Date:** 2026-09-16  

---

## 1. Executive Summary

Phase 1.4 regenerated, verified, and froze the final Part-1 `predictions.csv`.
All verification checks passed.

| Check | Result |
| :--- | :--- |
| `make run` regeneration | PASS |
| Official validator (`validate_submission.py`) | PASS |
| Internal validator (`gateway_priority.validation`) | PASS |
| Baseline parity (120/120 exact rows) | PASS |
| pytest (33/33) | PASS |
| pyright (0 errors, 0 warnings) | PASS |
| Determinism (MD5 identical across runs) | PASS |
| Alternate data-path portability | PASS |
| Secret/hardcoded-path safety | PASS |
| No raw-data modifications | PASS |

---

## 2. Submission Contract Verification

`predictions.csv` satisfies every constraint in `validate_submission.py`:

| Property | Value |
| :--- | :--- |
| Shape | 120 rows × 5 columns |
| Column order | `week_start`, `rank`, `gateway_id`, `score`, `reason` |
| Weeks | 8 (2026-02-02 through 2026-03-23) |
| Rows per week | 15 |
| Rank values per week | 1–15, no duplicates |
| Duplicate gateways per week | 0 |
| Score dtype | `float64` |
| All scores finite | Yes |
| No missing scores | Yes |
| Reason max length | 120 characters (limit: 300) |
| Unnamed index column | No |

---

## 3. Score Range

| Metric | `predictions.csv` | `predictions_baseline.csv` |
| :--- | :--- | :--- |
| Min score | 15.0 | 15.0 |
| Max score | 43.0 | 43.0 |
| Mean score | 22.608 | 22.608 |
| Median score | 21.0 | 21.0 |
| Unique values | 24 | 24 |

**Score range context:** The top-15-selected gateway scores range from 15 to 43 flagged hours.
Across all ~2,400 ranked gateways (before the top-15 cutoff), scores range from 0 to 43.
The maximum possible score is 168 hours (7 days × 24 hours), but no gateway reaches it.

---

## 4. Baseline Parity

| Metric | Matching | Total | Parity |
| :--- | :--- | :--- | :--- |
| Week match | 120 | 120 | 100.00% |
| Rank match | 120 | 120 | 100.00% |
| Gateway match | 120 | 120 | 100.00% |
| Score match | 120 | 120 | 100.00% |
| Reason match | 120 | 120 | 100.00% |
| **Exact row match** | **120** | **120** | **100.00%** |

---

## 5. Determinism

| Run | MD5 (`predictions.csv`) |
| :--- | :--- |
| Run 1 | `fbd532fe4364809a9cae5c218f0f8841` |
| Run 2 | `fbd532fe4364809a9cae5c218f0f8841` |

Identical output across consecutive regeneration runs.

---

## 6. Portability

Pipeline was executed with an alternate data directory path:

```bash
python -m gateway_priority.pipeline --data /alternate/path --out /alternate/predictions.csv
```

Output was byte-identical to `predictions.csv` produced with the default `--data data` path.

---

## 7. Safety Checks

- **No hardcoded absolute paths** in `src/`, `scripts/`, or `tests/`.
- **`.gitignore` protects `data/`** from accidental tracking.
- **`data/` directory unchanged** — verified against original state.
- **`baseline_3sigma.py`** — untouched.
- **`validate_submission.py`** — untouched.

---

## 8. Protected File Integrity

| File | Status |
| :--- | :--- |
| `baseline_3sigma.py` | UNTOUCHED |
| `validate_submission.py` | UNTOUCHED |
| `data/` (all raw files) | UNTOUCHED |

---

## 9. Phase Completion Summary

| Phase | Status |
| :--- | :--- |
| 1.1 — Baseline reproduction | PASS |
| 1.2 — Data audit | PASS |
| 1.2A — Audit/data-safety corrections | PASS |
| 1.3 — Reliable prediction pipeline | PASS |
| **1.4 — Final prediction freeze** | **PASS** |

---

## 10. Next Steps

Part 1 is now **complete and frozen**. Ready to proceed to Part 2 when instructed.
