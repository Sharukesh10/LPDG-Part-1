# Part 1 — Phase 1.2A: Data Audit Report (Corrected)

## Executive Summary
This report documents the empirical audit of all supplied datasets for the LPDG Innovation Hub Selection Challenge 2026. This updated Phase 1.2A revision corrects previous window-overlap terminology, adds safe data loading primitives, categorises telemetry duplicate keys, documents engineer review point-in-time constraints, and structures findings into confirmed quality issues, temporal risks, baseline limitations, observed non-material behavior, and open modeling questions.

---

## 1. Dataset Inventory Summary

| Dataset | Format | Total Rows | Total Cols | Unique Gateways (Norm) | Duplicate Rows | Min Date / Timestamp | Max Date / Timestamp |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `gateway_master.csv` | CSV (Latin-1) | 332 | 12 | 332 | 0 | 2019-03-04 | 2026-07-14 |
| `field_visits.csv` | CSV (UTF-8) | 642 | 8 | 247 | 0 | 2025-02-05 | 2026-02-14 |
| `meter_read_success.csv` | CSV (UTF-8) | 7,226 | 4 | 299 | 0 | 2025-08-04 | 2026-01-26 |
| `engineer_review_2026-02.xlsx` | XLSX | 120 | 6 | 120 | 0 | 2026-02-15 | 2026-02-15 |
| `telemetry/` (8 months Parquet) | Parquet | 1,433,387 | 5 | 320 | 6,547 | 2025-08-01 00:00:00+00:00 | 2026-03-31 23:00:00+00:00 |

---

## 2. Gateway ID Normalisation & Canonicalisation

- **CONFIRMED FACT**: Canonical Format is a 12-character uppercase hex string (e.g., `0639EA5602C1`).
- **Safe Loader & Helper**: Implemented in `gateway_priority.ids` (`normalize_gateway_id`, `canonicalize_gateway_id_series`) and `gateway_priority.data` (`load_gateway_master`).
- **Validation**: Fails cleanly with an explicit `ValueError` reporting row index and column when malformed non-null gateway IDs are encountered.
- **Unit Test Status**: 100% passed in `tests/test_ids.py` and `tests/test_data.py`.

---

## 3. Cross-Dataset Reconciliation

| Data Source | Unique Canonical Gateways | Gateways Missing from `gateway_master.csv` |
| :--- | :--- | :--- |
| `gateway_master.csv` | 332 | 0 (Reference Master) |
| `telemetry` (Parquet) | 320 | 0 |
| `field_visits.csv` | 247 | 0 |
| `meter_read_success.csv` | 299 | 0 |
| `engineer_review_2026-02.xlsx` | 120 | 0 |

- **CONFIRMED FACT**: Exactly **0** gateways in telemetry, field visits, meter reads, or engineer review exist outside `gateway_master.csv`.

---

## 4. Duplicate Telemetry Key Analysis & Materiality Experiment

Deep inspection of `(gateway_id, ts_utc)` duplicate composite keys across 8 months of telemetry parquet files:

- **CONFIRMED FACT**: Duplicate Key Groups = 6,547
- **CONFIRMED FACT**: Total Rows Belonging to Duplicate Groups = 13,094
- **CONFIRMED FACT**: Excess Duplicate Rows (`total_rows - total_groups`) = 6,547
- **CONFIRMED FACT**: Exact Duplicate Groups = 6,547 (rows where gateway ID, timestamp, and all metric values are identical)
- **CONFIRMED FACT**: Conflicting Duplicate Groups = 0 (rows where metric values differ for the same gateway and timestamp)
- **CONFIRMED FACT**: Exact Duplicate Rows = 13,094
- **CONFIRMED FACT**: Conflicting Duplicate Rows = 0
- **CONFIRMED FACT**: Affected Gateways = 293
- **CONFIRMED FACT**: Affected Telemetry Months = `2025-09,2025-11,2026-01`
- **CONFIRMED FACT**: Differing Metrics in Conflicting Duplicates = `None`

### Diagnostic Materiality Experiment (A: Raw Data vs B: Exact Duplicates Removed)
Comparing top-15 predictions of supplied baseline on (A) raw telemetry vs (B) exact duplicates removed:
- **Score Changes**: **0** score changes across all gateways.
- **Rank Changes**: **0** rank changes across all gateways.
- **Top-15 Membership Changes**: **0** swaps across all 8 scoring weeks.
- **Maximum Score Delta**: **0.0**
- **OBSERVATION**: Exact duplicates represent identical repeated telemetry records that fall symmetrically into both 28-day baseline reference and 7-day detection windows, resulting in zero net change to baseline anomaly flags or top-15 ranking.

---

## 5. Reference Window Construction & Overlap Diagnostics

### Correct Terminology
The supplied baseline uses:
- Reference window: $[T - 28\text{ days}, T)$
- Detection window: $[T - 7\text{ days}, T)$

The recent 7 days are contained inside the reference window, but **all observations are strictly before scoring Monday $T$**. Therefore, this is **NOT future-data leakage**.

Correct terminology for this behavior: **reference-window contamination**, **reference-window overlap**, or **self-normalisation**.

### Impact Explanation
- **OBSERVATION**: The overlap reduces anomaly sensitivity because recent abnormal observations influence the mean and standard deviation against which those recent observations are evaluated.
- **CONFIRMED FACT**: Changing reference construction to a non-overlapping 21-day window $[T - 28\text{d}, T - 7\text{d})$ alters top-15 gateway selection by **4 to 7 gateways per week** across all 8 scoring weeks.
- **DECISION REQUIRED**: We do NOT conclude that the separated window is superior at this stage; evaluating window structures requires Part 2 operational outcome and cost modeling.

---

## 6. Gateway Lifecycle & Active Filtering Diagnostics

- **CONFIRMED FACT**: Active definition: `installed_on <= T` AND (`decommissioned_on` is NaT OR `decommissioned_on > T`).
- **CONFIRMED FACT**: Telemetry & Visits: 0 records found before installation or after decommission.
- **CONFIRMED FACT**: Restricting baseline predictions to gateways active at $T$ resulted in **0 baseline-selected inactive gateways** across all 8 scoring weeks (inactive gateway count = 0, inactive gateway IDs = None).

---

## 7. Zero-Standard-Deviation ($\sigma = 0$) Analysis

- **OBSERVATION**: 4 to 6 gateways per week have $\sigma = 0$ for baseline metrics over the trailing 28 days.
- **CONFIRMED FACT**: Zero actual anomaly breaches were suppressed by converting $\sigma = 0 \to \text{NaN}$ in the evaluation window.
- **Classification**: **OBSERVED BUT CURRENTLY NON-MATERIAL IN CURRENT DATASET**.

---

## 8. Score Ties & Ranking Boundary Analysis

- **CONFIRMED FACT**: Rank-15 score ties occur in **7 out of 8 scoring weeks** (`2026-02-09`, `2026-02-16`, `2026-02-23`, `2026-03-02`, `2026-03-09`, `2026-03-16`, `2026-03-23`), with 3 to 4 gateways sharing the exact cutoff score at rank 15.
- **Classification**: **BASELINE DESIGN LIMITATIONS / RANKING AMBIGUITY**. Baseline insertion order remains the reference behavior for Part 1.

---

## 9. Structured Audit Conclusions

### CONFIRMED DATA QUALITY ISSUES
1. **German Character Encoding in Master**: `gateway_master.csv` contains German characters (`Außenmast` containing Eszett `ß`) encoded in ISO-8859-1 (Latin-1) and fails standard UTF-8 parsing. [CONFIRMED FACT]
2. **Duplicate Telemetry Keys**: 6,547 duplicate key groups (13,094 total rows, 6,547 excess rows) exist in telemetry parquet files. All 13,094 rows are exact duplicates; zero conflicting duplicates exist. [CONFIRMED FACT]

### CONFIRMED TEMPORAL RISKS
1. **Engineer Review Future Leakage**: `engineer_review_2026-02.xlsx` is dated **2026-02-15**. It is point-in-time unavailable for scoring Mondays `2026-02-02` and `2026-02-09`. Using it prior to `2026-02-16` constitutes future-data leakage. [CONFIRMED FACT]
2. **Point-in-Time Cutoff**: Predictions for Monday $T$ must strictly enforce `timestamp < T`. Data at or after $T$ must be excluded. [CONFIRMED FACT]

### BASELINE DESIGN LIMITATIONS
1. **Reference-Window Contamination**: Overlapping reference $[T-28\text{d}, T)$ and detection $[T-7\text{d}, T)$ windows self-normalise recent anomalies and alter top-15 selection by 4–7 gateways/week. [CONFIRMED FACT]
2. **Rank-15 Tie Sensitivity**: Severe score ties occur on the rank-15 boundary in 7/8 weeks, leaving selection dependent on arbitrary row ordering. [CONFIRMED FACT]

### OBSERVED BUT CURRENTLY NON-MATERIAL
1. **Zero-Standard-Deviation Handling**: Converting $\sigma = 0 \to \text{NaN}$ did not mask any actual anomaly breaches in this dataset. [CONFIRMED FACT]
2. **Exact Telemetry Duplicate Removal**: Removing exact duplicate rows produced zero score changes, zero rank changes, and zero top-15 swaps across all 8 weeks. [CONFIRMED FACT]
3. **Inactive Gateway Filtering**: Baseline selected zero inactive gateways across all 8 scoring weeks. [CONFIRMED FACT]

### OPEN MODELLING QUESTIONS FOR PART 2
1. **Missing Telemetry Hours**: Whether silent missing telemetry hours should increase gateway risk. [HYPOTHESIS / DECISION REQUIRED]
2. **Reference Window Separation**: Whether separating reference and detection windows improves operational visit cost/outcomes. [HYPOTHESIS / DECISION REQUIRED]
3. **Business Tie-Breakers**: Developing operational tie-breakers (e.g. meter read success rate, trend) for tied rankings. [DECISION REQUIRED]
