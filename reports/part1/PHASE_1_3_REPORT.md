# Phase 1.3: Reliable Prediction Pipeline Report

**Status:** PASS  
**Phase:** 1.3 — Reliable Prediction Pipeline  
**Date:** 2026-09-16  

---

## 1. Executive Summary

Phase 1.3 successfully reimplemented the supplied 3-sigma anomaly baseline as a modular, reproducible python package (`gateway_priority`).

- **Official Validator (`validate_submission.py`):** PASS
- **Internal Validation (`gateway_priority.validation`):** PASS
- **Baseline Parity (`predictions.csv` vs `predictions_baseline.csv`):** **100.00% exact row parity**
- **Test Suite (`pytest`):** **33/33 PASS**
- **Type Checking (`pyright`):** **0 errors, 0 warnings**
- **Determinism:** 100% reproducible across repeated executions.

---

## 2. Architecture & Design

The prediction pipeline is structured under `src/gateway_priority/` using standard setuptools src-layout packaging:

```
src/gateway_priority/
├── __init__.py      # Package entry & exports
├── config.py        # Centralized constants (SCORED_WEEKS, BASELINE_DAYS, RECENT_DAYS, SIGMA, METRICS)
├── ids.py           # Canonical gateway ID normalization (12-char upper-case hex)
├── data.py          # Safe data loading & point-in-time primitives
├── baseline.py      # Core 3-sigma anomaly ranking algorithm
├── validation.py    # Internal 5-column contract & range schema validator
└── pipeline.py      # CLI entry point (argparse execution flow)
```

### Key Principles Applied:
- **No Unnecessary Abstractions:** Avoided factory classes, repositories, or complex frameworks.
- **Strict Point-in-Time Isolation:** Telemetry filtering guarantees `timestamp < Monday_T` for each scoring week.
- **Preserved Supplied Semantics:** Overlapping 28-day reference window and 7-day detection window preserved exactly to match baseline specification.
- **No Part 2 Feature Creep:** Excluded engineer review, meter reads, lifecycle filtering, and ML algorithms.

---

## 3. Run Commands & CLI Specifications

### One-Command Execution
```bash
make run
```

### Modular Pipeline CLI Execution
```bash
python -m gateway_priority.pipeline --data data --out predictions.csv
```

### Official Submission Validation
```bash
python validate_submission.py predictions.csv
```

### Automated Unit Testing & Type Checking
```bash
pytest
pyright src/gateway_priority scripts/audit_data.py tests
```

---

## 4. Baseline Parity Results

Comparison of all 120 generated rows in `predictions.csv` against supplied `predictions_baseline.csv`:

| Metric | Matching Rows | Total Rows | Parity % |
| :--- | :--- | :--- | :--- |
| **Gateway-Set Parity** | 120 | 120 | **100.00%** |
| **Rank Parity** | 120 | 120 | **100.00%** |
| **Score Parity** | 120 | 120 | **100.00%** |
| **Reason Parity** | 120 | 120 | **100.00%** |
| **Exact Row Parity** | 120 | 120 | **100.00%** |

---

## 5. Test Suite & Validation Breakdown

### Unit & Integration Test Suite (`pytest`)
- **Total Tests:** 33
- **Passed:** 33
- **Failed:** 0

**Key Test Coverage Added in Phase 1.3:**
- `test_baseline.py`: Synthetic score calculation, point-in-time boundary isolation (`timestamp == T` and `timestamp > T` excluded), zero-std behavior.
- `test_validation.py`: Strict schema validation, duplicate detection, score bounds, non-finite handling, reason string length checks.
- `test_pipeline.py`: End-to-end CLI integration, output generation, missing argument failure paths.

---

## 6. Determinism & Stability Verification

Execution was performed multiple times with identical inputs and configuration:
- Run 1 vs Run 2 SHA256 checksum match: **Identical (`predictions.csv`)**
- Ordering stability: Rank cutoff ties (observed in 7/8 scoring weeks) were preserved consistently by preserving pandas stable dataframe sorting (`sort_values("flagged_hours", ascending=False)`).

---

## 7. Protected Files & Integrity Status

- `baseline_3sigma.py`: **UNTOUCHED / UNCHANGED**
- `validate_submission.py`: **UNTOUCHED / UNCHANGED**
- `data/`: **UNTOUCHED / UNCHANGED**

---

## 8. Known Limitations & Part 2 Observations

1. **Rank Cutoff Score Ties:** In 7 out of 8 scoring weeks, gateways tied at the rank-15 cutoff score. Ties are resolved implicitly by pandas input dataframe row order. This behavior is documented and preserved for Part 1 reproduction, but represents an opportunity for a deterministic business tie-breaker in Part 2.
2. **Window Overlap:** The 28-day reference window includes the 7-day recent detection period. This self-normalization was documented in Phase 1.2A and will be evaluated under operational cost metrics in Part 2.

---

## 9. Next Steps

Phase 1.3 is complete and verified. Ready to proceed to Phase 1.4 when instructed.
